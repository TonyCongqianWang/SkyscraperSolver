#include <assert.h>
#include <string.h>
#include "puzzle_init.h"
#include "lookahead_dive.h"
#include "prune_lookahead.h"
#include "solution_storage.h"
#include "solution_info.h"
#include "tree_search.h"
#include "node_selection_transition.h"

static t_puzzle puzzle;

static void reset_puzzle(void)
{
    memset(&puzzle, 0, sizeof(puzzle));
    assert(init_puzzle(&puzzle, 4, 1));
}

static void test_block_nested_negative(void)
{
    t_node_transition tr;
    t_node_state before;
    t_node_count visited;

    reset_puzzle();
    init_node_transition(&tr);
    tr.cell_idx = 0;
    tr.cell_val = 1;
    puzzle.cur_node->is_in_neg_lookahead = 1;
    before = *puzzle.cur_node;
    visited = puzzle.nodes_visited;
    assert(do_l_ahead_dive_neg(&puzzle, tr, 2, g_check_constr) == -1);
    assert(memcmp(&before, puzzle.cur_node, sizeof(before)) == 0);
    assert(puzzle.nodes_visited == visited);
    free_solution_storage(&puzzle);
}

static void test_nested_dispatch_and_context_restore(void)
{
    t_lookahead_config cfg;
    t_lookahead_ctx outer;
    t_node_order *cache;
    int i;

    reset_puzzle();
    memset(&cfg, 0, sizeof(cfg));
    memset(&outer, 0, sizeof(outer));
    cfg.selectivity = SELECTIVITY_NONE;
    cfg.max_depth = 1;
    cfg.lookahead_side = LOOKAHEAD_SIDE_BOTH;
    cfg.check_mode = g_check_constr;
    puzzle.cur_node->is_in_neg_lookahead = 1;
    puzzle.cur_node->is_in_lookahead_select = 1;
    puzzle.cur_node->lookahead_selectivity = SELECTIVITY_ANY_CHANGE;
    puzzle.cur_node->lookahead_ctx = &outer;
    run_lookahead_loop(&puzzle, puzzle.cur_node, &cfg);
    assert(puzzle.cur_node->is_in_neg_lookahead == 1);
    assert(puzzle.cur_node->is_in_lookahead_select == 1);
    assert(puzzle.cur_node->lookahead_selectivity == SELECTIVITY_ANY_CHANGE);
    assert(puzzle.cur_node->lookahead_ctx == &outer);
    cache = puzzle.cur_node->order_cache;
    for (i = 0; i < cache->count; ++i)
    {
        assert(cache->meta[i].entropy_pos >= 0);
        assert(cache->meta[i].entropy_neg == -1);
    }
    free_solution_storage(&puzzle);
}

static void test_regular_dfs_branching_allowed(void)
{
    t_search_frame frames[2];
    int depth;

    reset_puzzle();
    puzzle.cur_node->is_in_neg_lookahead = 1;
    puzzle.cur_node->cur_depth = 1;
    puzzle.cur_node->max_depth = 3;
    puzzle.cur_node->remaining_entropy = 0;
    init_sol_info(&frames[0].node_sols, puzzle.squared_size, 0);
    depth = 0;
    assert(process_frame(&puzzle, &depth, 0, frames) == SEARCH_CONTINUE);
    assert(depth == 1);
    assert(puzzle.cur_node == &puzzle.node_stack[1]);
    assert(puzzle.cur_node->is_in_neg_lookahead == 1);
    free_solution_storage(&puzzle);
}

int main(void)
{
    test_block_nested_negative();
    test_nested_dispatch_and_context_restore();
    test_regular_dfs_branching_allowed();
    return (0);
}
