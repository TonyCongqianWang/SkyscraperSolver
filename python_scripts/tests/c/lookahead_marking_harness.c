#include <assert.h>
#include <string.h>
#include "puzzle_init.h"
#include "puzzle_solver.h"
#include "search_context.h"
#include "lookahead_marks.h"
#include "solution_storage.h"
#include "node_selection.h"
#include "node_selection_cache.h"
#include "node_selection_transition.h"
#include "tree_search.h"

static t_solver_state puzzle;

static t_node_transition next_value(int cell, int value)
{
    t_node_transition next;
    init_node_transition(&next);
    next.cell_idx = cell;
    next.cell_val = value;
    return next;
}

static void reset(int limit)
{
    memset(&puzzle, 0, sizeof(puzzle));
    assert(init_puzzle(&puzzle, 4, limit));
}

static void prepare(t_lookahead_ctx *ctx, t_search_scope *scope)
{
    t_node_select_config config;
    int i;
    config.criterion = SELECT_MAX;
    config.rebuild_period = 0;
    config.selectivity = SELECTIVITY_NONE;
    rebuild_cache_if_stale(&puzzle, &config, 1);
    enter_lookahead(puzzle.cur_node, ctx, SELECTIVITY_NONE, scope);
    ctx->probe_pass = LOOKAHEAD_POS;
    for (i = 0; i < puzzle.squared_size; ++i)
        ctx->cell_passes[i] = 1;
}

static void test_marks_only_successful_probe_leaves(void)
{
    t_lookahead_ctx ctx;
    t_search_scope scope;
    t_probe_request request;
    t_node_state saved;
    t_node_transition next;

    reset(0);
    prepare(&ctx, &scope);
    request.next = next_value(0, 1);
    request.depth = 3;
    request.check_mode = g_check_constr;
    assert(enter_probe(&puzzle, &request, &saved));
    assert(!is_lookahead_assignment_marked(&ctx, request.next));
    assert(set_cell_invalid(&puzzle, 15, 1, g_check_none));
    assert(set_cell_invalid(&puzzle, 15, 2, g_check_none));
    assert(set_cell_invalid(&puzzle, 15, 3, g_check_none));
    assert(puzzle.cur_node->domain.vals[15] == 4);
    assert(!is_lookahead_assignment_marked(&ctx, next_value(15, 4)));
    enter_search_child(&puzzle, next_value(5, 2), 0);
    assert(!puzzle.cur_node->domain.is_invalid);
    enter_search_child(&puzzle, next_value(10, 3), 0);
    assert(!puzzle.cur_node->domain.is_invalid);
    (void)handle_leaf_node(&puzzle);
    assert(is_lookahead_assignment_marked(&ctx, request.next));
    assert(is_lookahead_assignment_marked(&ctx, next_value(15, 4)));
    assert(is_lookahead_assignment_marked(&ctx, next_value(5, 2)));
    assert(is_lookahead_assignment_marked(&ctx, next_value(10, 3)));
    leave_search_child(&puzzle);
    leave_search_child(&puzzle);
    leave_probe(&puzzle, &saved);
    assert(memcmp(&saved, puzzle.cur_node, sizeof(saved)) == 0);
    init_node_transition(&next);
    while (get_next_lookahead(&puzzle, &next))
        assert(!is_lookahead_assignment_marked(&ctx, next));
    leave_lookahead(puzzle.cur_node, &scope);
    free_solution_storage(&puzzle);
}

static void test_failed_probe_does_not_mark(void)
{
    t_lookahead_ctx ctx;
    t_search_scope scope;
    t_probe_request request;
    t_node_state saved;

    reset(0);
    prepare(&ctx, &scope);
    request.next = next_value(0, 1);
    request.depth = 3;
    request.check_mode = g_check_constr;
    assert(enter_probe(&puzzle, &request, &saved));
    puzzle.cur_node->domain.is_invalid = 1;
    (void)handle_leaf_node(&puzzle);
    assert(!is_lookahead_assignment_marked(&ctx, request.next));
    leave_probe(&puzzle, &saved);
    leave_lookahead(puzzle.cur_node, &scope);
    free_solution_storage(&puzzle);
}

static void test_depth_one_preserves_probe_eligibility(void)
{
    t_lookahead_ctx outer, inner;
    t_search_scope outer_scope, inner_scope;
    t_node_transition next;
    int count, i;

    reset(0);
    prepare(&outer, &outer_scope);
    enter_lookahead(puzzle.cur_node, &inner, SELECTIVITY_NONE, &inner_scope);
    inner.positive_probe_depth = 1;
    inner.probe_pass = LOOKAHEAD_POS;
    for (i = 0; i < puzzle.squared_size; ++i)
        inner.cell_passes[i] = 1;
    inner.explored_assignments[0] = 0xffff;
    assert(!is_lookahead_assignment_marked(&inner, next_value(0, 1)));
    init_node_transition(&next);
    count = 0;
    while (get_next_lookahead(&puzzle, &next))
        ++count;
    assert(count == 64);
    assert(inner.parent == &outer);
    assert(!is_lookahead_assignment_marked(&outer, next_value(0, 1)));
    leave_lookahead(puzzle.cur_node, &inner_scope);
    assert(puzzle.cur_node->lookahead_ctx == &outer);
    leave_lookahead(puzzle.cur_node, &outer_scope);
    free_solution_storage(&puzzle);
}

static void test_context_stack_and_reuse(void)
{
    t_lookahead_ctx *outer, *inner;
    t_search_scope outer_scope, inner_scope;

    reset(0);
    outer = &puzzle.lookahead_stack[0];
    inner = &puzzle.lookahead_stack[1];
    prepare(outer, &outer_scope);
    puzzle.cur_node->tree.lookahead_depth = 1;
    enter_lookahead(puzzle.cur_node, inner, SELECTIVITY_NONE, &inner_scope);
    inner->probe_pass = LOOKAHEAD_POS;
    inner->positive_probe_depth = 3;
    inner->probe_nesting_depth = 1;
    assert(inner->parent == outer);
    puzzle.cur_node->domain.vals[5] = 2;
    mark_lookahead_leaf(puzzle.cur_node);
    assert(is_lookahead_assignment_marked(inner, next_value(5, 2)));
    assert(!is_lookahead_assignment_marked(outer, next_value(5, 2)));
    leave_lookahead(puzzle.cur_node, &inner_scope);
    assert(puzzle.cur_node->lookahead_ctx == outer);
    enter_lookahead(puzzle.cur_node, inner, SELECTIVITY_NONE, &inner_scope);
    inner->probe_pass = LOOKAHEAD_POS;
    inner->positive_probe_depth = 3;
    assert(!is_lookahead_assignment_marked(inner, next_value(5, 2)));
    leave_lookahead(puzzle.cur_node, &inner_scope);
    leave_lookahead(puzzle.cur_node, &outer_scope);
    free_solution_storage(&puzzle);
}

static void test_solution_counts_and_unique_storage(int limit)
{
    t_sol_count i, j;
    int row, col, rmask, cmask;
    reset(limit);
    assert(solve_puzzle(&puzzle, -1) == (limit < 576 ? limit : 576));
    for (i = 0; i < puzzle.solutions_found; ++i)
    {
        assert(puzzle.solutions[i].domain.is_complete);
        assert(!puzzle.solutions[i].domain.is_invalid);
        for (row = 0; row < 4; ++row)
        {
            rmask = 0; cmask = 0;
            for (col = 0; col < 4; ++col)
            {
                rmask |= 1 << (puzzle.solutions[i].domain.vals[row*4+col]-1);
                cmask |= 1 << (puzzle.solutions[i].domain.vals[col*4+row]-1);
            }
            assert(rmask == 15 && cmask == 15);
        }
        for (j = 0; j < i; ++j)
            assert(memcmp(puzzle.solutions[i].domain.vals,
                          puzzle.solutions[j].domain.vals, 16) != 0);
    }
    free_solution_storage(&puzzle);
}

int main(void)
{
    test_marks_only_successful_probe_leaves();
    test_failed_probe_does_not_mark();
    test_depth_one_preserves_probe_eligibility();
    test_context_stack_and_reuse();
    test_solution_counts_and_unique_storage(1);
    test_solution_counts_and_unique_storage(2);
    test_solution_counts_and_unique_storage(600);
    return 0;
}
