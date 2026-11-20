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
#include "node_selection_eval.h"

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
    count = cache->items.count;
    for (i = 0; i < count; i++)
        cache->items.meta[i].cached_br_score = -(double)i;
    cache->items.meta[1].cached_br_score = 100;
    memcpy(before, cache->items.entries, sizeof(before));
    compact_stamp = cache->state.refresh_entropy[ORDER_COMPACT];
    sort_stamp = cache->state.refresh_entropy[ORDER_SORT];
    node_order_finish_lookahead(puzzle.cur_node, LOOKAHEAD_BOTH);
    assert(cache->state.scores_dirty);
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(!cache->state.scores_dirty && cache->items.count == count);
    assert(cache->items.entries[1].score > cache->items.entries[0].score);
    assert(cache->state.order_dirty);
    for (i = 0; i < count; i++)
    {
        assert(cache->items.entries[i].cell_idx == before[i].cell_idx);
        assert(cache->items.entries[i].cell_val == before[i].cell_val);
    }
    assert(cache->state.refresh_entropy[ORDER_SORT] == sort_stamp);
    assert(cache->state.refresh_entropy[ORDER_COMPACT] == compact_stamp);
    config.refresh_period[ORDER_SORT] = 0;
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(cache->items.entries[0].cell_idx == before[1].cell_idx);
    assert(cache->items.entries[0].cell_val == before[1].cell_val);
    assert(cache->items.meta[0].cached_br_score == 100);
    assert(!cache->state.order_dirty && cache->state.order_criterion == SELECT_MAX);
    recalculate_cache_scores(puzzle.cur_node, cache);
    assert(!cache->state.order_dirty);  /* Identical recomputation stays clean. */
    cache->state.refresh_entropy[ORDER_SORT] = puzzle.cur_node->domain.remaining_entropy + 1;
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(cache->state.refresh_entropy[ORDER_SORT] == puzzle.cur_node->domain.remaining_entropy);
    assert(!cache->state.order_dirty);  /* A skipped sort still advances its clock. */
    config.criterion = SELECT_MIN;
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(cache->state.order_criterion == SELECT_MIN);
    assert(cache->items.entries[0].score < cache->items.entries[count - 1].score);
    config.criterion = SELECT_MAX;
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(cache->state.order_criterion == SELECT_MAX);
    assert(cache->items.meta[0].cached_br_score == 100);
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
    old_count = cache->items.count;
    memcpy(stamps, cache->state.refresh_entropy, sizeof(stamps));
    set_cell_val(&puzzle, 0, 1, g_check_constr);
    config.refresh_period[ORDER_COMPACT] = 0;
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(cache->items.count < old_count);
    for (i = ORDER_RESCORE; i < ORDER_REFRESH_COUNT; i++)
        assert(cache->state.refresh_entropy[i] == stamps[i]);
    old_count = cache->items.count;
    cache->items.meta[0].cached_br_score = -100;
    config.refresh_period[ORDER_COMPACT] = INT_MAX;
    config.refresh_period[ORDER_RESCORE] = 0;
    rebuild_cache_if_stale(&puzzle, &config, 1);
    assert(cache->items.count == old_count);
    assert(cache->items.meta[0].cached_br_score != -100);
    assert(!cache->state.scores_dirty);
    assert(cache->state.refresh_entropy[ORDER_RESCORE] == puzzle.cur_node->domain.remaining_entropy);
    assert(cache->state.refresh_entropy[ORDER_BLEND] == puzzle.cur_node->domain.remaining_entropy);
    assert(cache->state.refresh_entropy[ORDER_SORT] == stamps[ORDER_SORT]);
    assert(cache->state.refresh_entropy[ORDER_LINES] == stamps[ORDER_LINES]);
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
    assert(!puzzle.cur_node->order_cache->state.scores_dirty);
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
    assert(memcmp(puzzle.cur_node->order_cache->items.entries, before.items.entries, sizeof(before.items.entries)) == 0);
    free_solution_storage(&puzzle);
}

static void test_period_scales_are_size_specific(void)
{
    t_node_select_config other;
    double *controls[] = {&g_sel_period_scale_le7, &g_sel_compact_period_le7,
        &g_sel_rescore_period_le7, &g_sel_blend_period_le7, &g_sel_sort_period_le7,
        &g_sel_line_sort_period_le7, &g_sel_period_scale_s8, &g_sel_sort_period_s9};
    double saved[8];
    int i;

    /* Routing checks use fixtures rather than optimizer-controlled defaults. */
    for (i = 0; i < 8; i++)
    {
        saved[i] = *controls[i];
        *controls[i] = 1;
    }
    g_sel_period_scale_s8 = 2.5;
    g_sel_sort_period_s9 = 4.5;
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
    assert(get_sel_period_scale(8) == 2.5);
    assert(get_cache_period_scale(9, ORDER_SORT) == 4.5);
    puzzle.cur_node->domain.remaining_entropy = 1;
    g_sel_period_scale_le7 = 16;
    g_sel_sort_period_le7 = 16;
    select_node_select_config(&puzzle, &other);
    assert(other.refresh_period[ORDER_COMPACT] == INT_MAX);
    assert(other.refresh_period[ORDER_SORT] == INT_MAX);
    for (i = 0; i < 8; i++)
        *controls[i] = saved[i];
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
