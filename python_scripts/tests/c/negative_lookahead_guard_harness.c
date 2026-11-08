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
    puzzle.cur_node->tree.neg_lookahead_depth = 1;
    before = *puzzle.cur_node;
    visited = puzzle.nodes_visited;
    assert(probe_exclusion(&puzzle, tr, 2, g_check_constr).status == DIVE_SKIP);
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
    cfg.passes = LOOKAHEAD_BOTH;
    cfg.check_mode = g_check_constr;
    puzzle.cur_node->tree.neg_lookahead_depth = 1;
    puzzle.cur_node->search_policy.branch.is_in_lookahead_select = 1;
    puzzle.cur_node->search_policy.branch.lookahead_selectivity = SELECTIVITY_ANY_CHANGE;
    puzzle.cur_node->lookahead_ctx = &outer;
    run_lookahead(&puzzle, puzzle.cur_node, &cfg);
    assert(puzzle.cur_node->tree.neg_lookahead_depth == 1);
    assert(puzzle.cur_node->search_policy.branch.is_in_lookahead_select == 1);
    assert(puzzle.cur_node->search_policy.branch.lookahead_selectivity == SELECTIVITY_ANY_CHANGE);
    assert(puzzle.cur_node->lookahead_ctx == &outer);
    assert(cfg.passes == LOOKAHEAD_BOTH);
    cache = puzzle.cur_node->order_cache;
    assert(cache->lookahead_build_entropy == -1);
    assert(cache->needs_rebuild == 0);
    for (i = 0; i < cache->count; ++i)
    {
        assert(cache->meta[i].entropy_pos >= 0);
        assert(cache->meta[i].entropy_neg == -1);
    }
    free_solution_storage(&puzzle);
}

static void test_nested_negative_side_skips_all_passes(void)
{
    t_lookahead_config cfg;
    t_node_order *cache;
    t_node_count visited;

    reset_puzzle();
    memset(&cfg, 0, sizeof(cfg));
    cfg.selectivity = SELECTIVITY_NONE;
    cfg.max_depth = 1;
    cfg.passes = LOOKAHEAD_NEG;
    cfg.check_mode = g_check_constr;
    puzzle.cur_node->tree.neg_lookahead_depth = 1;
    cache = puzzle.cur_node->order_cache;
    visited = puzzle.nodes_visited;
    run_lookahead(&puzzle, puzzle.cur_node, &cfg);
    assert(cfg.passes == LOOKAHEAD_NEG);
    assert(puzzle.nodes_visited == visited);
    assert(cache == puzzle.cur_node->order_cache);
    assert(cache->count == 0);
    assert(cache->lookahead_build_entropy == -1);
    assert(cache->needs_rebuild == 0);
    free_solution_storage(&puzzle);
}

static void test_subnode_both_sides_does_not_mark_cache(void)
{
    t_lookahead_config cfg;
    t_node_order *cache;
    int i;

    reset_puzzle();
    memset(&cfg, 0, sizeof(cfg));
    cfg.selectivity = SELECTIVITY_NONE;
    cfg.max_depth = 1;
    cfg.passes = LOOKAHEAD_BOTH;
    cfg.check_mode = g_check_constr;
    puzzle.cur_node->tree.lookahead_depth = 1;
    run_lookahead(&puzzle, puzzle.cur_node, &cfg);
    cache = puzzle.cur_node->order_cache;
    assert(cache->count == 64);
    assert(cache->lookahead_build_entropy == -1);
    assert(cache->needs_rebuild == 0);
    for (i = 0; i < cache->count; ++i)
    {
        assert(cache->meta[i].entropy_pos >= 0);
        assert(cache->meta[i].entropy_neg >= 0);
    }
    free_solution_storage(&puzzle);
}

static void test_regular_dfs_branching_allowed(void)
{
    t_search_frame frames[2];
    t_search_policy parent_policy;
    int depth;

    reset_puzzle();
    puzzle.cur_node->tree.neg_lookahead_depth = 1;
    puzzle.cur_node->cur_depth = 1;
    puzzle.cur_node->search_policy.limits.max_depth = 3;
    puzzle.cur_node->remaining_entropy = 0;
    puzzle.cur_node->search_policy.branch.is_in_lookahead_select = 1;
    puzzle.cur_node->search_policy.branch.lookahead_selectivity = SELECTIVITY_ANY_CHANGE;
    parent_policy = puzzle.cur_node->search_policy;
    init_sol_info(&frames[0].node_sols, puzzle.squared_size, 0);
    depth = 0;
    assert(process_frame(&puzzle, &depth, 0, frames) == SEARCH_CONTINUE);
    assert(depth == 1);
    assert(puzzle.cur_node == &puzzle.node_stack[1]);
    assert(puzzle.cur_node->tree.neg_lookahead_depth == 1);
    assert(puzzle.cur_node->search_policy.branch.is_in_lookahead_select
        == parent_policy.branch.is_in_lookahead_select);
    assert(puzzle.cur_node->search_policy.branch.lookahead_selectivity
        == parent_policy.branch.lookahead_selectivity);
    assert(puzzle.cur_node->search_policy.limits.max_depth
        == parent_policy.limits.max_depth);
    assert(puzzle.node_stack[0].search_policy.limits.max_solutions
        == parent_policy.limits.max_solutions);
    free_solution_storage(&puzzle);
}

static void test_nesting_limits(void)
{
    t_node_transition tr;
    t_node_state before;
    t_node_count visited;
    t_lookahead_config cfg;

    reset_puzzle();
    init_node_transition(&tr);
    tr.cell_idx = 0;
    tr.cell_val = 1;
    puzzle.cur_node->tree.lookahead_depth = MAX_LOOKAHEAD_DEPTH;
    before = *puzzle.cur_node;
    visited = puzzle.nodes_visited;
    assert(probe_assumption(&puzzle, tr, 1, g_check_constr).status == DIVE_SKIP);
    assert(probe_exclusion(&puzzle, tr, 1, g_check_constr).status == DIVE_SKIP);
    assert(memcmp(&before, puzzle.cur_node, sizeof(before)) == 0);
    assert(puzzle.nodes_visited == visited);
    memset(&cfg, 0, sizeof(cfg));
    cfg.selectivity = SELECTIVITY_NONE;
    cfg.passes = LOOKAHEAD_BOTH;
    cfg.max_depth = 1;
    cfg.check_mode = g_check_constr;
    run_lookahead(&puzzle, puzzle.cur_node, &cfg);
    assert(puzzle.nodes_visited == visited);
    puzzle.cur_node->tree.lookahead_depth = MAX_LOOKAHEAD_DEPTH - 1;
    puzzle.cur_node->tree.neg_lookahead_depth = MAX_NEG_LOOKAHEAD_DEPTH;
    before = *puzzle.cur_node;
    assert(probe_exclusion(&puzzle, tr, 1, g_check_constr).status == DIVE_SKIP);
    assert(memcmp(&before, puzzle.cur_node, sizeof(before)) == 0);
    free_solution_storage(&puzzle);
}

int main(void)
{
    test_block_nested_negative();
    test_nested_dispatch_and_context_restore();
    test_nested_negative_side_skips_all_passes();
    test_subnode_both_sides_does_not_mark_cache();
    test_regular_dfs_branching_allowed();
    test_nesting_limits();
    return (0);
}
