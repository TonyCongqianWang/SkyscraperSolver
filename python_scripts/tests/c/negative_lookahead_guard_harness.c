#include <assert.h>
#include <string.h>
#include "puzzle_init.h"
#include "lookahead_dive.h"
#include "prune_lookahead.h"
#include "solution_storage.h"
#include "solution_info.h"
#include "tree_search.h"
#include "search_context.h"
#include "search_result.h"
#include "grid_availability.h"
#include "node_selection.h"
#include "node_selection_transition.h"

static t_solver_state puzzle;

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
    cfg.depth.positive = 1;
    cfg.depth.negative = 1;
    cfg.passes = LOOKAHEAD_BOTH;
    cfg.check_mode = g_check_constr;
    puzzle.cur_node->tree.neg_lookahead_depth = 1;
    puzzle.cur_node->search_policy.branch.eligibility = CANDIDATES_LOOKAHEAD;
    outer.selectivity = SELECTIVITY_ANY_CHANGE;
    puzzle.cur_node->search_policy.mode = SEARCH_LOOKAHEAD;
    puzzle.cur_node->lookahead_ctx = &outer;
    run_lookahead(&puzzle, puzzle.cur_node, &cfg);
    assert(puzzle.cur_node->tree.neg_lookahead_depth == 1);
    assert(puzzle.cur_node->search_policy.branch.eligibility == CANDIDATES_LOOKAHEAD);
    assert(outer.selectivity == SELECTIVITY_ANY_CHANGE);
    assert(puzzle.cur_node->lookahead_ctx == &outer);
    assert(puzzle.cur_node->search_policy.mode == SEARCH_LOOKAHEAD);
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
    cfg.depth.positive = 1;
    cfg.depth.negative = 1;
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
    cfg.depth.positive = 1;
    cfg.depth.negative = 1;
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
    t_lookahead_ctx outer;
    int depth;

    reset_puzzle();
    memset(&outer, 0, sizeof(outer));
    puzzle.cur_node->lookahead_ctx = &outer;
    puzzle.cur_node->tree.neg_lookahead_depth = 1;
    puzzle.cur_node->tree.depth = 1;
    puzzle.cur_node->search_policy.limits.max_depth = 3;
    puzzle.cur_node->domain.remaining_entropy = 0;
    puzzle.cur_node->search_policy.branch.eligibility = CANDIDATES_VALID;
    outer.selectivity = SELECTIVITY_ANY_CHANGE;
    parent_policy = puzzle.cur_node->search_policy;
    init_sol_info(&frames[0].node_sols, 1, 0);
    frames[0].registered_start = puzzle.solutions_found;
    depth = 0;
    assert(process_search_frame(&puzzle, &depth, 0, frames) == SEARCH_CONTINUE);
    assert(depth == 1);
    assert(puzzle.cur_node == &puzzle.node_stack[1]);
    assert(puzzle.cur_node->tree.neg_lookahead_depth == 1);
    assert(puzzle.cur_node->search_policy.branch.eligibility
        == parent_policy.branch.eligibility);
    assert(puzzle.cur_node->lookahead_ctx == &outer);
    assert(outer.selectivity == SELECTIVITY_ANY_CHANGE);
    assert(puzzle.cur_node->search_policy.limits.max_depth
        == parent_policy.limits.max_depth);
    assert(puzzle.node_stack[0].search_policy.limits.max_solutions
        == parent_policy.limits.max_solutions);
    free_solution_storage(&puzzle);
}

static void test_probe_scope_and_leaf_states(void)
{
    t_node_state saved;
    t_search_scope scope;
    t_lookahead_ctx cursor;
    t_probe_request request;

    reset_puzzle();
    assert(classify_search_leaf(puzzle.cur_node) == LEAF_NONE);
    enter_lookahead(puzzle.cur_node, &cursor, SELECTIVITY_NONE, &scope);
    assert(puzzle.node_stack_top == 0);
    assert(puzzle.cur_node->search_policy.mode == SEARCH_LOOKAHEAD);
    assert(puzzle.cur_node->search_policy.branch.cache_refresh == CACHE_REFRESH_REQUIRED);
    assert(puzzle.cur_node->search_policy.branch.eligibility == CANDIDATES_LOOKAHEAD);
    assert(cursor.selectivity == SELECTIVITY_NONE);
    init_node_transition(&request.next);
    request.next.cell_idx = 0;
    request.next.cell_val = 1;
    request.check_mode = g_check_constr;
    request.depth = -2;
    assert(enter_probe(&puzzle, &request, &saved));
    assert(puzzle.cur_node->tree.depth == saved.tree.depth + 1);
    assert(!is_valid_value(puzzle.cur_node, 0, 1));
    assert(puzzle.cur_node->search_policy.mode == SEARCH_DFS);
    assert(puzzle.cur_node->search_policy.branch.cache_refresh == CACHE_REFRESH_STALE);
    assert(puzzle.cur_node->search_policy.branch.eligibility == CANDIDATES_VALID);
    assert(puzzle.cur_node->lookahead_ctx == &cursor);
    assert(puzzle.cur_node->tree.neg_lookahead_depth == 1);
    assert(puzzle.cur_node->tree.lookahead_depth == 1);
    puzzle.cur_node->tree.depth = puzzle.cur_node->search_policy.limits.max_depth;
    assert(classify_search_leaf(puzzle.cur_node) == LEAF_DEPTH_LIMIT);
    puzzle.cur_node->domain.is_complete = 1;
    assert(classify_search_leaf(puzzle.cur_node) == LEAF_COMPLETE);
    puzzle.cur_node->domain.is_invalid = 1;
    assert(classify_search_leaf(puzzle.cur_node) == LEAF_INVALID);
    leave_probe(&puzzle, &saved);
    assert(memcmp(&saved, puzzle.cur_node, sizeof(saved)) == 0);
    leave_lookahead(puzzle.cur_node, &scope);
    assert(puzzle.cur_node->search_policy.mode == SEARCH_DFS);
    assert(puzzle.cur_node->search_policy.branch.eligibility == CANDIDATES_VALID);
    assert(puzzle.cur_node->lookahead_ctx == NULL);
    free_solution_storage(&puzzle);
}

static void test_eligibility_independent_of_cache_refresh(void)
{
    t_lookahead_ctx ctx;
    t_search_scope saved;
    t_node_order *cache;
    t_node_transition next;
    int stale_entropy;

    reset_puzzle();
    memset(&ctx, 0, sizeof(ctx));
    enter_lookahead(puzzle.cur_node, &ctx, SELECTIVITY_VALUE_SET, &saved);
    cache = puzzle.cur_node->order_cache;
    cache->count = 2;
    cache->build_depth = 0;
    stale_entropy = puzzle.cur_node->domain.remaining_entropy + 1000000;
    cache->last_build_entropy = stale_entropy;
    cache->entries[0].cell_idx = 0;
    cache->entries[0].cell_val = 1;
    cache->entries[0].score = 100;
    cache->entries[1].cell_idx = 1;
    cache->entries[1].cell_val = 1;
    cache->entries[1].score = 50;
    ctx.cell_passes[0] = 3;
    ctx.cell_passes[1] = 1;
    puzzle.cur_node->search_policy.branch.eligibility = CANDIDATES_VALID;
    init_node_transition(&next);
    assert(try_select_transition(&puzzle, &next));
    assert(next.cell_idx == 0);
    assert(ctx.curr_index == 0 && ctx.curr_pass == 0);
    assert(cache->last_build_entropy == stale_entropy);
    puzzle.cur_node->search_policy.branch.eligibility = CANDIDATES_LOOKAHEAD;
    init_node_transition(&next);
    assert(try_select_transition(&puzzle, &next));
    assert(next.cell_idx == 1);
    assert(!try_select_transition(&puzzle, &next));
    assert(cache->last_build_entropy == stale_entropy);
    puzzle.cur_node->search_policy.branch.eligibility = CANDIDATES_VALID;
    puzzle.cur_node->search_policy.branch.cache_refresh = CACHE_REFRESH_STALE;
    assert(try_select_transition(&puzzle, &next));
    assert(cache->last_build_entropy == puzzle.cur_node->domain.remaining_entropy);
    assert(ctx.curr_pass == 2);
    leave_lookahead(puzzle.cur_node, &saved);
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
    cfg.depth.positive = 1;
    cfg.depth.negative = 1;
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
    test_eligibility_independent_of_cache_refresh();
    test_probe_scope_and_leaf_states();
    test_nesting_limits();
    test_block_nested_negative();
    test_nested_dispatch_and_context_restore();
    test_nested_negative_side_skips_all_passes();
    test_subnode_both_sides_does_not_mark_cache();
    test_regular_dfs_branching_allowed();
    return (0);
}
