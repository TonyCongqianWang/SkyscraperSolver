#include <assert.h>
#include <string.h>
#include "line_order.h"
#include "entropy.h"
#include "puzzle_init.h"
#include "node_selection_cache.h"
#include "node_selection_transition.h"
#include "node_selection_eval.h"
#include "solution_storage.h"
#include "lookahead_dive.h"
#include "check_node_validity.h"
#include "selectivity.h"

static t_puzzle puzzle;

static void reset_puzzle(int size)
{
    memset(&puzzle, 0, sizeof(puzzle));
    init_puzzle(&puzzle, size, 1);
}

static void set_line_count(t_node_state *node, int line, int count)
{
    int value;

    for (value = 0; value < node->size; value++)
        node->constrs.num_val_positions[line][value] = count;
}

static void check_order(t_node_state *node)
{
    t_line_order *order = get_line_order(node);
    int seen[MAX_N_CONSTR_PAIRS] = {0};
    int i;
    int id;

    assert(order->count == 2 * node->size);
    for (i = 0; i < order->count; i++)
    {
        id = order->entries[i].constr_idx;
        assert(id >= 0 && id < 2 * node->size && !seen[id]);
        seen[id] = 1;
        assert(order->entries[i].entropy == compute_constr_entropy(node, id, node->size));
        if (i > 0)
            assert(order->entries[i - 1].entropy <= order->entries[i].entropy);
    }
}

static t_node_select_config selection_config(void)
{
    t_node_select_config config;

    memset(&config, 0, sizeof(config));
    config.criterion = SELECT_MAX;
    config.selectivity = SELECTIVITY_NONE;
    return config;
}

static void test_initialization_and_stability(void)
{
    int size;
    int i;
    t_line_order snapshot;

    for (size = 4; size <= MAX_SIZE; size++)
    {
        reset_puzzle(size);
        check_order(puzzle.cur_node);
        for (i = 0; i < 2 * size; i++)
            assert(get_line_order(puzzle.cur_node)->entries[i].constr_idx == i);
        for (i = 0; i < 2 * size; i++)
            set_line_count(puzzle.cur_node, i, (i % size) + 1);
        sort_line_order(puzzle.cur_node);
        check_order(puzzle.cur_node);
        snapshot = *get_line_order(puzzle.cur_node);
        for (i = 0; i < 2 * size; i++)
            set_line_count(puzzle.cur_node, i, size);
        sort_line_order(puzzle.cur_node);
        for (i = 0; i < 2 * size; i++)
            assert(get_line_order(puzzle.cur_node)->entries[i].constr_idx == snapshot.entries[i].constr_idx);
        free_solution_storage(&puzzle);
    }
}

static void test_lazy_build_rebuild_and_compaction(void)
{
    t_node_select_config config = selection_config();
    t_line_order snapshot;

    reset_puzzle(4);
    snapshot = *get_line_order(puzzle.cur_node);
    set_line_count(puzzle.cur_node, 5, 1);
    assert(memcmp(get_line_order(puzzle.cur_node), &snapshot, sizeof(snapshot)) == 0);
    build_node_order(&puzzle, &config);
    assert(puzzle.order_stack.top_idx == 1);
    assert(memcmp(&puzzle.line_order_stack.orders[0], &snapshot, sizeof(snapshot)) == 0);
    check_order(puzzle.cur_node);
    assert(get_line_order(puzzle.cur_node)->entries[0].constr_idx == 5);
    set_line_count(puzzle.cur_node, 2, 1);
    set_line_count(puzzle.cur_node, 5, 4);
    build_node_order(&puzzle, &config);
    assert(puzzle.order_stack.top_idx == 1);
    check_order(puzzle.cur_node);
    assert(get_line_order(puzzle.cur_node)->entries[0].constr_idx == 2);
    set_line_count(puzzle.cur_node, 7, 1);
    set_line_count(puzzle.cur_node, 2, 4);
    compact_and_sort_cache(puzzle.cur_node, puzzle.cur_node->order_cache, SELECT_MAX);
    check_order(puzzle.cur_node);
    assert(get_line_order(puzzle.cur_node)->entries[0].constr_idx == 7);
    free_solution_storage(&puzzle);
}

static void test_branch_isolation_and_restoration(void)
{
    t_node_select_config config = selection_config();
    t_line_order parent_order;
    t_node_order parent_cache;

    reset_puzzle(4);
    build_node_order(&puzzle, &config);
    parent_order = *get_line_order(puzzle.cur_node);
    parent_cache = *puzzle.cur_node->order_cache;
    puzzle.node_stack[1] = puzzle.node_stack[0];
    puzzle.cur_node = &puzzle.node_stack[1];
    puzzle.cur_node->cur_depth = 1;
    puzzle.node_stack_top = 1;
    set_line_count(puzzle.cur_node, 6, 1);
    assert(get_line_order(puzzle.cur_node) == &puzzle.line_order_stack.orders[1]);
    assert(memcmp(get_line_order(puzzle.cur_node), &parent_order, sizeof(parent_order)) == 0);
    build_node_order(&puzzle, &config);
    assert(puzzle.order_stack.top_idx == 2);
    check_order(puzzle.cur_node);
    assert(get_line_order(puzzle.cur_node)->entries[0].constr_idx == 6);
    assert(memcmp(&puzzle.line_order_stack.orders[1], &parent_order, sizeof(parent_order)) == 0);
    assert(memcmp(&puzzle.order_stack.orders[1], &parent_cache, sizeof(parent_cache)) == 0);
    puzzle.cur_node = &puzzle.node_stack[0];
    puzzle.node_stack_top = 0;
    sync_cache_stacks(&puzzle);
    assert(puzzle.order_stack.top_idx == 1);
    assert(memcmp(get_line_order(puzzle.cur_node), &parent_order, sizeof(parent_order)) == 0);
    puzzle.node_stack[1] = puzzle.node_stack[0];
    puzzle.cur_node = &puzzle.node_stack[1];
    puzzle.cur_node->cur_depth = 1;
    build_node_order(&puzzle, &config);
    check_order(puzzle.cur_node);
    assert(memcmp(get_line_order(puzzle.cur_node), &parent_order, sizeof(parent_order)) == 0);
    free_solution_storage(&puzzle);
}

static void test_lookahead_restoration(void)
{
    t_node_select_config config = selection_config();
    t_node_transition next;
    t_line_order snapshot;
    int old_top;

    reset_puzzle(4);
    build_node_order(&puzzle, &config);
    init_node_transition(&next);
    assert(get_best_from_cache(&puzzle, &next, &config));
    snapshot = *get_line_order(puzzle.cur_node);
    old_top = puzzle.order_stack.top_idx;
    do_l_ahead_dive(&puzzle, next, 2, g_check_constr);
    assert(puzzle.order_stack.top_idx == old_top);
    assert(puzzle.cur_node->cur_depth == 0);
    assert(memcmp(get_line_order(puzzle.cur_node), &snapshot, sizeof(snapshot)) == 0);
    do_l_ahead_dive_neg(&puzzle, next, 2, g_check_constr);
    assert(puzzle.order_stack.top_idx == old_top);
    assert(puzzle.cur_node->cur_depth == 0);
    assert(memcmp(get_line_order(puzzle.cur_node), &snapshot, sizeof(snapshot)) == 0);
    free_solution_storage(&puzzle);
}

static void test_live_selectivity(void)
{
    t_node_state *node;
    int i;

    reset_puzzle(4);
    node = puzzle.cur_node;
    node->rows_changed_since_prune = 0;
    node->cols_changed_since_prune = 0;
    node->rows_invalid_since_prune = 0;
    node->cols_invalid_since_prune = 0;
    for (i = 0; i < 8; i++)
    {
        assert(should_process_line(node, i, SELECTIVITY_NONE));
        assert(!should_process_line(node, i, SELECTIVITY_VALUE_SET));
        assert(!should_process_line(node, i, SELECTIVITY_ANY_CHANGE));
    }
    node->cols_changed_since_prune = 1 << 2;
    node->rows_changed_since_prune = 1 << 1;
    node->cols_invalid_since_prune = 1 << 0;
    node->rows_invalid_since_prune = 1 << 3;
    for (i = 0; i < 8; i++)
    {
        assert(should_process_line(node, i, SELECTIVITY_VALUE_SET) == (i == 2 || i == 5));
        assert(should_process_line(node, i, SELECTIVITY_ANY_CHANGE) == (i == 0 || i == 2 || i == 5 || i == 7));
    }
    free_solution_storage(&puzzle);
}

int main(void)
{
    test_initialization_and_stability();
    test_lazy_build_rebuild_and_compaction();
    test_branch_isolation_and_restoration();
    test_lookahead_restoration();
    test_live_selectivity();
    return 0;
}
