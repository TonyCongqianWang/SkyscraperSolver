#include <assert.h>
#include <string.h>
#include "puzzle_init.h"
#include "tree_search.h"
#include "search_context.h"
#include "search_result.h"
#include "solution_info.h"
#include "solution_storage.h"
#include "lookahead_dive.h"

static t_solver_state puzzle;

static void reset(int size, int limit, int depth)
{
    memset(&puzzle, 0, sizeof(puzzle));
    assert(init_puzzle(&puzzle, size, limit));
    puzzle.cur_node->tree.depth = depth;
}

static void test_leaf_depths(void)
{
    t_sol_info result;

    reset(4, 0, 5);
    puzzle.cur_node->search_policy.limits.max_depth = 5;
    result = tree_search(&puzzle);
    assert(result.min_valid_depth == 5 && !result.exhausted);
    /* A node invalidated by pruning contributes its parent depth. */
    puzzle.cur_node->domain.is_invalid = 1;
    result = tree_search(&puzzle);
    assert(result.min_valid_depth == 4 && result.exhausted);
    free_solution_storage(&puzzle);

    reset(4, 0, 0);
    puzzle.cur_node->domain.is_invalid = 1;
    result = tree_search(&puzzle);
    assert(result.min_valid_depth == -1 && result.exhausted);
    free_solution_storage(&puzzle);

    reset(2, 1, 3);
    set_cell_val(&puzzle, 0, 1, g_check_constr);
    assert(puzzle.cur_node->domain.is_complete);
    result = tree_search(&puzzle);
    assert(result.min_valid_depth == 3 && result.solutions_registered == 1);
    free_solution_storage(&puzzle);
}

static void test_failed_transitions(void)
{
    t_probe_result result;
    t_node_transition next;
    t_node_state before;

    reset(4, 9, 5);
    /* Forbid a hypothesis without making the parent invalid. */
    set_cell_invalid(&puzzle, 0, 1, g_check_constr);
    memset(&next, 0, sizeof(next));
    next.cell_val = 1;
    before = *puzzle.cur_node;
    result = probe_assumption(&puzzle, next, 2, g_check_constr);
    assert(result.status == DIVE_FAIL);
    assert(result.outcome.min_valid_depth == 5);
    assert(result.outcome.solutions_registered == 0);
    assert(memcmp(&before, puzzle.cur_node, sizeof(before)) == 0);
    free_solution_storage(&puzzle);

    reset(4, 0, 5);
    set_cell_val(&puzzle, 0, 1, g_check_constr);
    before = *puzzle.cur_node;
    result = probe_exclusion(&puzzle, next, 2, g_check_constr);
    assert(result.status == DIVE_FAIL);
    assert(result.outcome.min_valid_depth == 5);
    assert(result.outcome.solutions_registered == 0);
    assert(memcmp(&before, puzzle.cur_node, sizeof(before)) == 0);
    free_solution_storage(&puzzle);
}

static void test_budget_inheritance_and_nested_restoration(void)
{
    t_probe_request request;
    t_node_state outer;
    t_node_state inner;
    t_sol_info result;
    int limit;

    for (limit = 0; limit <= 9; limit += 9)
    {
        reset(4, limit, 3);
        memset(&request, 0, sizeof(request));
        request.depth = 2;
        request.next.cell_val = 1;
        request.check_mode = g_check_constr;
        assert(enter_probe(&puzzle, &request, &outer));
        assert(puzzle.cur_node->search_policy.limits.max_solutions == (t_sol_count)limit);
        assert(puzzle.cur_node->tree.depth == 4);
        set_cell_invalid(&puzzle, 1, 4, g_check_constr);
        assert(!puzzle.cur_node->domain.is_invalid);
        request.next.cell_idx = 1;
        request.next.cell_val = 4;
        assert(enter_probe(&puzzle, &request, &inner));
        assert(puzzle.cur_node->tree.depth == 5);
        assert(puzzle.cur_node->domain.is_invalid);
        assert(puzzle.cur_node->search_policy.limits.max_solutions == (t_sol_count)limit);
        result = handle_leaf_node(&puzzle);
        assert(result.min_valid_depth == 4 && result.exhausted);
        leave_probe(&puzzle, &inner);
        assert(memcmp(&inner, puzzle.cur_node, sizeof(inner)) == 0);
        leave_probe(&puzzle, &outer);
        assert(memcmp(&outer, puzzle.cur_node, sizeof(outer)) == 0);
        free_solution_storage(&puzzle);
    }
}

static void test_child_budget_and_bounded_return(void)
{
    t_node_transition next;
    t_probe_request request;
    t_node_state saved;
    t_sol_info result;

    reset(4, 9, 2);
    memset(&next, 0, sizeof(next));
    next.cell_val = 1;
    enter_search_child(&puzzle, next, 2);
    assert(puzzle.cur_node->search_policy.limits.max_solutions == 7);
    request.next = next;
    request.next.cell_idx = 1;
    request.next.cell_val = 2;
    request.depth = -2;
    request.check_mode = g_check_constr;
    assert(enter_probe(&puzzle, &request, &saved));
    assert(puzzle.cur_node->search_policy.limits.max_solutions == 7);
    assert(puzzle.cur_node->tree.neg_lookahead_depth == 1);
    leave_probe(&puzzle, &saved);
    assert(memcmp(&saved, puzzle.cur_node, sizeof(saved)) == 0);
    leave_search_child(&puzzle);
    assert(puzzle.cur_node->search_policy.limits.max_solutions == 9);
    free_solution_storage(&puzzle);

    reset(4, 0, 3);
    puzzle.cur_node->search_policy.limits.max_depth = 4;
    result = tree_search(&puzzle);
    assert(result.min_valid_depth == 4);
    assert(!result.exhausted && result.solutions_registered == 0);
    assert(puzzle.cur_node->tree.depth == 3);
    puzzle.cur_node->tree.lookahead_depth = MAX_LOOKAHEAD_DEPTH;
    result = probe_assumption(&puzzle, next, 1, g_check_constr).outcome;
    assert(result.min_valid_depth == VALID_DEPTH_UNSET);
    free_solution_storage(&puzzle);
}

static void test_aggregation_and_loop_exit(void)
{
    t_sol_info aggregate;
    t_sol_info child;

    reset(4, 0, 2);
    init_sol_info(&aggregate, 1, 2);
    assert(aggregate.min_valid_depth == VALID_DEPTH_UNSET);
    init_sol_info(&child, 0, 0);
    child.min_valid_depth = 8;
    update_sol_info(&child, &aggregate);
    assert(aggregate.min_valid_depth == 8);
    child.min_valid_depth = 5;
    update_sol_info(&child, &aggregate);
    assert(aggregate.min_valid_depth == 5);
    child.min_valid_depth = 9;
    update_sol_info(&child, &aggregate);
    assert(aggregate.min_valid_depth == 5);
    child.min_valid_depth = VALID_DEPTH_UNSET;
    update_sol_info(&child, &aggregate);
    assert(aggregate.min_valid_depth == 5);
    assert(!aggregate.exhausted && aggregate.solutions_registered == 2);
    puzzle.cur_node->search_policy.branch.eligibility = CANDIDATES_LOOKAHEAD;
    finish_candidate_search(&aggregate, puzzle.cur_node);
    assert(aggregate.min_valid_depth == 5);
    init_sol_info(&aggregate, 1, 0);
    finish_candidate_search(&aggregate, puzzle.cur_node);
    assert(aggregate.min_valid_depth == 2);
    child.min_valid_depth = 6;
    aggregate.min_valid_depth = 6;
    puzzle.cur_node->domain.is_invalid = 1;
    finish_candidate_search(&aggregate, puzzle.cur_node);
    assert(aggregate.min_valid_depth == 1 && aggregate.exhausted);
    /* An invalid root's -1 contribution is real, not an unset marker. */
    child.min_valid_depth = -1;
    update_sol_info(&child, &aggregate);
    assert(aggregate.min_valid_depth == -1);
    child.min_valid_depth = VALID_DEPTH_UNSET;
    update_sol_info(&child, &aggregate);
    assert(aggregate.min_valid_depth == -1);
    free_solution_storage(&puzzle);
}

static void test_pruning_collapse_before_return(void)
{
    t_search_frame frames[1];
    int depth = 0;

    reset(4, 1, 3);
    init_sol_info(&frames[0].node_sols, 0, 1);
    frames[0].node_sols.min_valid_depth = 8;
    puzzle.cur_node->domain.is_invalid = 1;
    assert(check_backtrack(&puzzle, &depth, 0, frames) == SEARCH_TERMINATE);
    assert(frames[0].node_sols.min_valid_depth == 2);
    assert(frames[0].node_sols.solutions_registered == 1);
    assert(!frames[0].node_sols.exhausted);
    free_solution_storage(&puzzle);
}

int main(void)
{
    test_pruning_collapse_before_return();
    test_leaf_depths();
    test_failed_transitions();
    test_budget_inheritance_and_nested_restoration();
    test_child_budget_and_bounded_return();
    test_aggregation_and_loop_exit();
    return (0);
}
