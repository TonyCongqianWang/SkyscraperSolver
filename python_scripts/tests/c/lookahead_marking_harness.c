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
#include "grid_interface.h"

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
    ctx->positive_probe_depth = 3;
    for (i = 0; i < puzzle.squared_size; ++i)
        ctx->cell_passes[i] = 1;
}

static void test_path_marks_survive_restoration(void)
{
    t_lookahead_ctx ctx;
    t_search_scope scope;
    t_probe_request request;
    t_node_state saved;
    t_node_transition next;
    t_sol_info outcome;
    t_lookahead_config config;
    int count, i;

    reset(0);
    prepare(&ctx, &scope);
    request.next = next_value(0, 1);
    request.depth = 3;
    request.check_mode = g_check_constr;
    assert(enter_probe(&puzzle, &request, &saved));
    enter_search_child(&puzzle, next_value(1, 2), 0);
    enter_search_child(&puzzle, next_value(2, 3), 0);
    leave_search_child(&puzzle);
    leave_search_child(&puzzle);
    leave_probe(&puzzle, &saved);
    assert(memcmp(&saved, puzzle.cur_node, sizeof(saved)) == 0);
    assert(is_lookahead_assignment_marked(&ctx, next_value(0, 1)));
    assert(is_lookahead_assignment_marked(&ctx, next_value(1, 2)));
    assert(is_lookahead_assignment_marked(&ctx, next_value(2, 3)));
    /* Unassigned values must not have marks. */
    assert(!is_lookahead_assignment_marked(&ctx, next_value(3, 4)));
    assert(!is_lookahead_assignment_marked(&ctx, next_value(1, 3)));
    init_node_transition(&next);
    count = 0;
    while (get_next_lookahead(&puzzle, &next))
    {
        assert(!is_lookahead_assignment_marked(&ctx, next));
        ++count;
    }
    {
        int cell, val, marked;

        marked = 0;
        for (cell = 0; cell < puzzle.squared_size; ++cell)
            for (val = 1; val <= puzzle.size; ++val)
                marked += !!is_lookahead_assignment_marked(
                    &ctx, next_value(cell, val));
        assert(marked >= 3);
        assert(count == 64 - marked);
    }
    ctx.probe_pass = LOOKAHEAD_NEG;
    init_node_transition(&next);
    count = 0;
    while (get_next_lookahead(&puzzle, &next))
        ++count;
    assert(count == 64);
    /* A pool emptied only by marks is unresolved, never infeasible. */
    for (i = 0; i < puzzle.squared_size; ++i)
        ctx.explored_assignments[i] = 0xffff;
    memset(&config, 0, sizeof(config));
    config.depth.positive = 3;
    config.depth.negative = 3;
    config.check_mode = g_check_constr;
    outcome = run_tree_search(&puzzle, &config, LOOKAHEAD_POS);
    assert(!outcome.exhausted && outcome.solutions_registered == 0);
    assert(!puzzle.cur_node->domain.is_invalid);
    /* DFS must still select candidates even if all probe choices are marked. */
    puzzle.cur_node->search_policy.mode = SEARCH_DFS;
    puzzle.cur_node->search_policy.branch.eligibility = CANDIDATES_VALID;
    init_node_transition(&next);
    assert(try_select_transition(&puzzle, &next));
    assert(is_lookahead_assignment_marked(&ctx, next));
    leave_lookahead(puzzle.cur_node, &scope);
    free_solution_storage(&puzzle);
}

static void test_nested_marks_and_reset(void)
{
    t_lookahead_ctx outer, inner, fresh;
    t_search_scope outer_scope, inner_scope;
    t_node_transition next = next_value(5, 2);
    reset(0);
    prepare(&outer, &outer_scope);
    enter_lookahead(puzzle.cur_node, &inner, SELECTIVITY_NONE, &inner_scope);
    inner.probe_pass = LOOKAHEAD_POS;
    inner.positive_probe_depth = 3;
    assert(inner.parent == &outer);
    mark_lookahead_assignment(&inner, next);
    assert(is_lookahead_assignment_marked(&inner, next));
    assert(is_lookahead_assignment_marked(&outer, next));
    leave_lookahead(puzzle.cur_node, &inner_scope);
    assert(puzzle.cur_node->lookahead_ctx == &outer);
    assert(is_lookahead_assignment_marked(&outer, next));
    /* An exclusion is not an assignment mark; negative scopes don't inherit skips. */
    outer.probe_pass = LOOKAHEAD_NEG;
    mark_lookahead_assignment(&outer, next_value(6, 3));
    outer.probe_pass = LOOKAHEAD_POS;
    assert(!is_lookahead_assignment_marked(&outer, next_value(6, 3)));
    leave_lookahead(puzzle.cur_node, &outer_scope);
    prepare(&fresh, &outer_scope);
    assert(fresh.parent == NULL);
    assert(!is_lookahead_assignment_marked(&fresh, next));
    leave_lookahead(puzzle.cur_node, &outer_scope);
    free_solution_storage(&puzzle);
}


static void test_forced_assignment_marks(void)
{
    t_lookahead_ctx *ctx;
    t_search_scope scope;

    reset(0);
    ctx = &puzzle.lookahead_stack[0];
    prepare(ctx, &scope);
    assert(set_cell_invalid(&puzzle, 0, 1, g_check_none));
    assert(set_cell_invalid(&puzzle, 0, 2, g_check_none));
    assert(set_cell_invalid(&puzzle, 0, 3, g_check_none));
    assert(puzzle.cur_node->domain.vals[0] == 4);
    assert(is_lookahead_assignment_marked(ctx, next_value(0, 4)));
    assert(!is_lookahead_assignment_marked(ctx, next_value(0, 1)));
    leave_lookahead(puzzle.cur_node, &scope);
    free_solution_storage(&puzzle);
}

static void test_depth_one_preserves_probe_eligibility(void)
{
    t_lookahead_ctx *outer;
    t_lookahead_ctx *inner;
    t_search_scope outer_scope, inner_scope;
    t_node_transition next;
    int count;

    reset(0);
    outer = &puzzle.lookahead_stack[0];
    inner = &puzzle.lookahead_stack[1];
    prepare(outer, &outer_scope);
    enter_lookahead(puzzle.cur_node, inner, SELECTIVITY_NONE, &inner_scope);
    inner->positive_probe_depth = 1;
    inner->probe_pass = LOOKAHEAD_POS;
    for (count = 0; count < puzzle.squared_size; ++count)
        inner->cell_passes[count] = 1;
    mark_lookahead_assignment(inner, next_value(0, 1));
    assert(inner->parent == outer);
    assert(!is_lookahead_assignment_marked(inner, next_value(0, 1)));
    assert(is_lookahead_assignment_marked(outer, next_value(0, 1)));
    init_node_transition(&next);
    count = 0;
    while (get_next_lookahead(&puzzle, &next))
        ++count;
    assert(count == 64);
    leave_lookahead(puzzle.cur_node, &inner_scope);
    assert(puzzle.cur_node->lookahead_ctx == outer);
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
    test_path_marks_survive_restoration();
    test_forced_assignment_marks();
    test_depth_one_preserves_probe_eligibility();
    test_nested_marks_and_reset();
    test_solution_counts_and_unique_storage(1);
    test_solution_counts_and_unique_storage(2);
    test_solution_counts_and_unique_storage(600);
    return 0;
}
