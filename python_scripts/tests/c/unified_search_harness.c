#include <assert.h>
#include <string.h>
#include "puzzle_init.h"
#include "tree_search.h"
#include "search_context.h"
#include "solution_info.h"
#include "solution_storage.h"
#include "node_selection_cache.h"
#include "node_selection_transition.h"

static t_solver_state puzzle;

static void reset(t_lookahead_config *config)
{
    memset(&puzzle, 0, sizeof(puzzle));
    assert(init_puzzle(&puzzle, 4, 1));
    memset(config, 0, sizeof(*config));
    config->max_depth = 1;
    config->selectivity = SELECTIVITY_NONE;
    config->passes = LOOKAHEAD_BOTH;
    config->check_mode = g_check_constr;
}

static void prepare(t_lookahead_ctx *ctx, t_search_scope *scope)
{
    t_node_select_config order;
    int i;

    order.criterion = SELECT_MAX;
    order.rebuild_period = 0;
    order.selectivity = SELECTIVITY_NONE;
    rebuild_cache_if_stale(&puzzle, &order, 1);
    memset(ctx, 0, sizeof(*ctx));
    for (i = 0; i < puzzle.squared_size; ++i)
        ctx->cell_passes[i] = 1;
    enter_lookahead(puzzle.cur_node, ctx, SELECTIVITY_NONE, scope);
}

static void test_frame_cursor_progress(void)
{
    t_lookahead_config config;
    t_lookahead_ctx ctx;
    t_search_scope scope;
    t_search_frame frames[1];
    t_node_transition first;
    int d;

    reset(&config);
    prepare(&ctx, &scope);
    memset(frames, 0, sizeof(frames));
    init_sol_info(&frames[0].node_sols, 1, 0);
    init_node_transition(&frames[0].next);
    frames[0].probe_config = &config;
    frames[0].probe_pass = LOOKAHEAD_POS;
    d = 0;
    assert(process_frame(&puzzle, &d, 0, frames) == SEARCH_CONTINUE);
    assert(!frames[0].node_sols.exhausted);
    assert(frames[0].node_sols.solutions_registered == 0);
    first = frames[0].next;
    assert(puzzle.nodes_visited == 1);
    assert(process_frame(&puzzle, &d, 0, frames) == SEARCH_CONTINUE);
    assert(frames[0].next.cell_idx != first.cell_idx
        || frames[0].next.cell_val != first.cell_val);
    assert(puzzle.nodes_visited == 2);
    assert(puzzle.main_nodes_visited == 0);
    assert(d == 0 && puzzle.node_stack_top == 0);
    assert(puzzle.cur_node == &puzzle.node_stack[0]);
    assert(puzzle.cur_node->tree.depth == 0);
    assert(puzzle.cur_node->search_policy.mode == SEARCH_LOOKAHEAD);
    assert(puzzle.cur_node->lookahead_ctx == &ctx);
    leave_lookahead(puzzle.cur_node, &scope);
    free_solution_storage(&puzzle);
}

static void test_complete_passes(void)
{
    t_lookahead_config config;
    t_lookahead_ctx ctx;
    t_search_scope scope;
    t_sol_info result;
    t_node_state before;
    t_node_order *cache;
    int i;

    reset(&config);
    /* Lookahead is same-node traversal, not DFS at the parent's bound. */
    puzzle.cur_node->search_policy.limits.max_depth = 0;
    prepare(&ctx, &scope);
    before = *puzzle.cur_node;
    cache = puzzle.cur_node->order_cache;
    cache->last_build_entropy = puzzle.cur_node->domain.remaining_entropy + 1000000;
    result = run_tree_search(&puzzle, &config, LOOKAHEAD_POS);
    assert(!result.exhausted && result.solutions_registered == 0);
    assert(puzzle.nodes_visited == (t_node_count)cache->count);
    result = run_tree_search(&puzzle, &config, LOOKAHEAD_NEG);
    assert(!result.exhausted && result.solutions_registered == 0);
    assert(puzzle.nodes_visited == (t_node_count)(2 * cache->count));
    assert(puzzle.main_nodes_visited == 0 && puzzle.solutions_found == 0);
    assert(cache->last_build_entropy == before.domain.remaining_entropy + 1000000);
    for (i = 0; i < cache->count; ++i)
    {
        assert(cache->meta[i].entropy_pos >= 0);
        assert(cache->meta[i].entropy_neg >= 0);
    }
    assert(memcmp(&before.domain, &puzzle.cur_node->domain, sizeof(before.domain)) == 0);
    ctx.selectivity = SELECTIVITY_VALUE_SET;
    for (i = 0; i < puzzle.squared_size; ++i)
        ctx.cell_passes[i] = 3;
    result = run_tree_search(&puzzle, &config, LOOKAHEAD_POS);
    assert(!result.exhausted && result.solutions_registered == 0);
    assert(puzzle.nodes_visited == (t_node_count)(2 * cache->count));
    leave_lookahead(puzzle.cur_node, &scope);
    assert(puzzle.cur_node->search_policy.mode == SEARCH_DFS);
    assert(puzzle.cur_node->lookahead_ctx == NULL);
    assert(puzzle.cur_node->search_policy.limits.max_depth == 0);
    free_solution_storage(&puzzle);
}

static void test_same_node_terminal_outcomes(void)
{
    t_lookahead_config config;
    t_lookahead_ctx ctx;
    t_search_scope scope;
    t_sol_info result;

    reset(&config);
    prepare(&ctx, &scope);
    puzzle.cur_node->domain.is_complete = 1;
    result = run_tree_search(&puzzle, &config, LOOKAHEAD_POS);
    assert(!result.exhausted && result.solutions_registered == 0);
    assert(puzzle.nodes_visited == 0 && puzzle.solutions_found == 0);
    puzzle.cur_node->domain.is_invalid = 1;
    result = run_tree_search(&puzzle, &config, LOOKAHEAD_NEG);
    assert(result.exhausted && result.solutions_registered == 0);
    assert(puzzle.nodes_visited == 0 && puzzle.solutions_found == 0);
    leave_lookahead(puzzle.cur_node, &scope);
    free_solution_storage(&puzzle);
}

int main(void)
{
    test_frame_cursor_progress();
    test_complete_passes();
    test_same_node_terminal_outcomes();
    return (0);
}
