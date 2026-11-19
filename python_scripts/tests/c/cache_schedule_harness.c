#include <assert.h>
#include <limits.h>
#include <string.h>
#include "puzzle_init.h"
#include "solution_storage.h"
#include "node_selection_cache.h"
#include "node_selection_transition.h"
#include "node_selection_score.h"
#include "line_order.h"
#include "grid_interface.h"
#include "strategy_routing.h"
#include "params_cache_period.h"
#include "puzzle_solver.h"

static t_solver_state puzzle;
static t_node_select_config config;

static void reset(void)
{
    int i;
    memset(&puzzle, 0, sizeof(puzzle));
    memset(&config, 0, sizeof(config));
    init_puzzle(&puzzle, 4, 1);
    config.criterion = SELECT_MAX;
    for (i = 0; i < ORDER_REFRESH_COUNT; i++)
        config.refresh_period[i] = INT_MAX;
    build_node_order(&puzzle, &config);
}

static void test_probe_scores_do_not_reorder_or_recollect(void)
{
    t_node_order *cache;
    t_node_transition before[MAX_TRANSITIONS];
    int compact_stamp;
    int sort_stamp;
    int count;
    int i;
    reset();
    cache = puzzle.cur_node->order_cache;
    count = cache->count;
    for (i = 0; i < count; i++)
        cache->meta[i].cached_br_score = -(double)i;
    cache->meta[1].cached_br_score = 100;
    memcpy(before, cache->entries, sizeof(before));
    compact_stamp = cache->refresh_entropy[ORDER_COMPACT];
    sort_stamp = cache->refresh_entropy[ORDER_SORT];
    node_order_finish_lookahead(puzzle.cur_node, LOOKAHEAD_BOTH);
    assert(cache->scores_dirty);
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(!cache->scores_dirty && cache->count == count);
    assert(cache->entries[1].score > cache->entries[0].score);
    for (i = 0; i < count; i++)
    {
        assert(cache->entries[i].cell_idx == before[i].cell_idx);
        assert(cache->entries[i].cell_val == before[i].cell_val);
    }
    assert(cache->refresh_entropy[ORDER_SORT] == sort_stamp);
    assert(cache->refresh_entropy[ORDER_COMPACT] == compact_stamp);
    config.refresh_period[ORDER_SORT] = 0;
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(cache->entries[0].cell_idx == before[1].cell_idx);
    assert(cache->entries[0].cell_val == before[1].cell_val);
    assert(cache->meta[0].cached_br_score == 100);
    free_solution_storage(&puzzle);
}

static void test_independent_compact_and_score_clocks(void)
{
    t_node_order *cache;
    int stamps[ORDER_REFRESH_COUNT];
    int old_count;
    int i;
    reset();
    cache = puzzle.cur_node->order_cache;
    old_count = cache->count;
    memcpy(stamps, cache->refresh_entropy, sizeof(stamps));
    set_cell_val(&puzzle, 0, 1, g_check_constr);
    config.refresh_period[ORDER_COMPACT] = 0;
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(cache->count < old_count);
    for (i = ORDER_RESCORE; i < ORDER_REFRESH_COUNT; i++)
        assert(cache->refresh_entropy[i] == stamps[i]);
    old_count = cache->count;
    cache->meta[0].cached_br_score = -100;
    config.refresh_period[ORDER_COMPACT] = INT_MAX;
    config.refresh_period[ORDER_RESCORE] = 0;
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(cache->count == old_count);
    assert(cache->meta[0].cached_br_score != -100);
    assert(!cache->scores_dirty);
    assert(cache->refresh_entropy[ORDER_RESCORE] == puzzle.cur_node->domain.remaining_entropy);
    assert(cache->refresh_entropy[ORDER_BLEND] == puzzle.cur_node->domain.remaining_entropy);
    assert(cache->refresh_entropy[ORDER_SORT] == stamps[ORDER_SORT]);
    assert(cache->refresh_entropy[ORDER_LINES] == stamps[ORDER_LINES]);
    free_solution_storage(&puzzle);
}

static void test_dirty_score_update_preserves_parent_cache(void)
{
    t_node_order parent;
    t_line_order lines;
    reset();
    parent = *puzzle.cur_node->order_cache;
    lines = *get_line_order(puzzle.cur_node);
    puzzle.node_stack[1] = puzzle.node_stack[0];
    puzzle.cur_node = &puzzle.node_stack[1];
    puzzle.cur_node->tree.depth = 1;
    puzzle.node_stack_top = 1;
    isolate_node_order(&puzzle);
    assert(puzzle.order_stack.top_idx == 2);
    node_order_finish_lookahead(puzzle.cur_node, LOOKAHEAD_BOTH);
    rebuild_cache_if_stale(&puzzle, &config, 0);
    assert(!puzzle.cur_node->order_cache->scores_dirty);
    assert(memcmp(&puzzle.order_stack.orders[1], &parent, sizeof(parent)) == 0);
    assert(memcmp(&puzzle.line_order_stack.orders[1], &lines, sizeof(lines)) == 0);
    puzzle.cur_node = &puzzle.node_stack[0];
    puzzle.node_stack_top = 0;
    sync_cache_stacks(&puzzle);
    assert(puzzle.order_stack.top_idx == 1);
    assert(memcmp(puzzle.cur_node->order_cache, &parent, sizeof(parent)) == 0);
    free_solution_storage(&puzzle);
}

static void test_line_order_has_its_own_period(void)
{
    t_node_order before;
    t_line_order lines;
    int i;
    reset();
    before = *puzzle.cur_node->order_cache;
    lines = *get_line_order(puzzle.cur_node);
    for (i = 0; i < 4; i++)
        puzzle.cur_node->domain.constrs.num_val_positions[5][i] = 1;
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(memcmp(get_line_order(puzzle.cur_node), &lines, sizeof(lines)) == 0);
    config.refresh_period[ORDER_LINES] = 0;
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(get_line_order(puzzle.cur_node)->entries[0].constr_idx == 5);
    assert(memcmp(puzzle.cur_node->order_cache->entries, before.entries, sizeof(before.entries)) == 0);
    free_solution_storage(&puzzle);
}

static void test_period_scales_are_size_specific(void)
{
    t_node_select_config other;
    reset();
    puzzle.cur_node->domain.remaining_entropy = puzzle.max_entropy / 2;
    select_node_select_config(&puzzle, &config);
    g_sel_period_scale_le7 = 2;
    g_sel_sort_period_le7 = 3;
    select_node_select_config(&puzzle, &other);
    assert(other.refresh_period[ORDER_COMPACT] >= 2 * config.refresh_period[ORDER_COMPACT]);
    assert(other.refresh_period[ORDER_SORT] >= 3 * other.refresh_period[ORDER_COMPACT]);
    assert(other.refresh_period[ORDER_SORT] < 3 * other.refresh_period[ORDER_COMPACT] + 3);
    assert(other.refresh_period[ORDER_BLEND] == other.refresh_period[ORDER_COMPACT]);
    assert(get_sel_period_scale(8) == 1);
    assert(get_cache_period_scale(9, ORDER_SORT) == 1);
    puzzle.cur_node->domain.remaining_entropy = 1;
    g_sel_period_scale_le7 = 16;
    g_sel_sort_period_le7 = 16;
    select_node_select_config(&puzzle, &other);
    assert(other.refresh_period[ORDER_COMPACT] == INT_MAX);
    assert(other.refresh_period[ORDER_SORT] == INT_MAX);
    g_sel_period_scale_le7 = 1;
    g_sel_sort_period_le7 = 1;
    free_solution_storage(&puzzle);
}

static void test_solution_counts_with_independent_reuse(void)
{
    double *scales[] = {&g_sel_compact_period_le7, &g_sel_rescore_period_le7,
        &g_sel_blend_period_le7, &g_sel_sort_period_le7, &g_sel_line_sort_period_le7};
    int trial;
    int i;
    for (trial = 0; trial < 4; trial++)
    {
        memset(&puzzle, 0, sizeof(puzzle));
        init_puzzle(&puzzle, 4, 0);
        g_sel_period_scale_le7 = trial == 0 ? 0 : 16;
        for (i = 0; i < ORDER_REFRESH_COUNT; i++)
            *scales[i] = trial < 2 ? 1 : 16;
        if (trial == 2)
            g_sel_rescore_period_le7 = 0;
        if (trial == 3)
        {
            g_sel_compact_period_le7 = 0;
            g_sel_line_sort_period_le7 = 0;
        }
        solve_puzzle(&puzzle, -1);
        assert(puzzle.solutions_found == 576);
        free_solution_storage(&puzzle);
    }
    for (i = 0; i < ORDER_REFRESH_COUNT; i++)
        *scales[i] = 1;
    g_sel_period_scale_le7 = 1;
}

int main(void)
{
    test_probe_scores_do_not_reorder_or_recollect();
    test_independent_compact_and_score_clocks();
    test_dirty_score_update_preserves_parent_cache();
    test_line_order_has_its_own_period();
    test_period_scales_are_size_specific();
    test_solution_counts_with_independent_reuse();
    return 0;
}
