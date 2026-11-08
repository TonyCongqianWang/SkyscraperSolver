#include <assert.h>
#include <string.h>
#include "puzzle_init.h"
#include "tree_search.h"
#include "search_result.h"
#include "solution_info.h"
#include "solution_storage.h"
#include "grid_availability.h"
#include "lookahead_dive.h"

static t_solver_state puzzle;

static void reset(int size, int limit)
{
    memset(&puzzle, 0, sizeof(puzzle));
    assert(init_puzzle(&puzzle, size, limit));
}

static void check_result(t_sol_info result, t_sol_count registered, int exhausted)
{
    assert(result.solutions_registered == registered);
    assert(result.exhausted == exhausted);
}

static void test_leaves(void)
{
    t_sol_info result;
    reset(4, 1);
    puzzle.cur_node->search_policy.limits.max_depth = 0;
    check_result(tree_search(&puzzle), 0, 0);
    puzzle.cur_node->domain.is_invalid = 1;
    check_result(tree_search(&puzzle), 0, 1);
    free_solution_storage(&puzzle);

    reset(2, 1);
    set_cell_val(&puzzle, 0, 1, g_check_constr);
    assert(puzzle.cur_node->domain.is_complete);
    puzzle.cur_node->tree.lookahead_depth = 1;
    check_result(tree_search(&puzzle), 0, 0);
    assert(puzzle.solutions_found == 0);
    puzzle.cur_node->tree.lookahead_depth = 0;
    result = tree_search(&puzzle);
    check_result(result, 1, 1);
    assert(puzzle.solutions_found == 1);
    /* Rejected registration cannot certify a new invocation as exhausted. */
    check_result(handle_leaf_node(&puzzle), 0, 0);
    assert(puzzle.solutions_found == 1);
    free_solution_storage(&puzzle);
}

static void test_exhaustion_and_limits(void)
{
    t_sol_info result;
    reset(2, 0);
    result = tree_search(&puzzle);
    check_result(result, 2, 1);
    assert(puzzle.solutions_found == 2);
    free_solution_storage(&puzzle);

    reset(2, 1);
    check_result(tree_search(&puzzle), 1, 0);
    assert(puzzle.solutions_found == 1);
    free_solution_storage(&puzzle);

    reset(4, 0);
    puzzle.cur_node->search_policy.limits.max_depth = 1;
    check_result(tree_search(&puzzle), 0, 0);
    assert(puzzle.node_stack_top == 0);
    assert(puzzle.cur_node == &puzzle.node_stack[0]);
    assert(puzzle.solutions_found == 0);
    free_solution_storage(&puzzle);

    reset(4, 0);
    puzzle.cur_node->search_policy.limits.target_nunset = 16;
    assert(classify_search_leaf(puzzle.cur_node) == LEAF_PROGRESS_LIMIT);
    check_result(tree_search(&puzzle), 0, 0);
    free_solution_storage(&puzzle);
}

static void test_consumption(void)
{
    t_sol_info aggregate;
    t_sol_info child;
    t_result_transition transition;
    t_node_state before;
    int mode;

    for (mode = SEARCH_DFS; mode <= SEARCH_LOOKAHEAD; ++mode)
    {
        reset(4, 0);
        puzzle.cur_node->search_policy.mode = mode;
        transition.next.cell_idx = 0;
        transition.next.cell_val = 1;
        transition.is_neg = 0;
        before = *puzzle.cur_node;
        init_sol_info(&aggregate, 1, 2);
        init_sol_info(&child, 0, 0);
        consume_child_result(&puzzle, &transition, &child, &aggregate);
        check_result(aggregate, 2, 0);
        assert(memcmp(&before.domain, &puzzle.cur_node->domain, sizeof(before.domain)) == 0);
        init_sol_info(&child, 1, 3);
        consume_child_result(&puzzle, &transition, &child, &aggregate);
        check_result(aggregate, 5, 0);
        assert(!is_valid_value(puzzle.cur_node, 0, 1));
        free_solution_storage(&puzzle);
    }
    reset(4, 0);
    transition.is_neg = 1;
    init_sol_info(&child, 1, 0);
    consume_child_result(&puzzle, &transition, &child, NULL);
    assert(puzzle.cur_node->domain.vals[0] == 1);
    free_solution_storage(&puzzle);
}

static void test_restrictions_and_probe(void)
{
    t_sol_info result;
    t_node_transition next;
    t_probe_result probe;
    t_node_state before;

    reset(4, 0);
    init_sol_info(&result, 1, 2);
    puzzle.cur_node->search_policy.branch.eligibility = CANDIDATES_LOOKAHEAD;
    finish_candidate_search(&result, puzzle.cur_node);
    check_result(result, 2, 0);
    puzzle.cur_node->search_policy.branch.eligibility = CANDIDATES_VALID;
    finish_candidate_search(&result, puzzle.cur_node);
    check_result(result, 2, 0);
    init_sol_info(&result, 1, 2);
    finish_candidate_search(&result, puzzle.cur_node);
    check_result(result, 2, 1);
    memset(&next, 0, sizeof(next));
    next.cell_val = 1;
    before = *puzzle.cur_node;
    probe = probe_assumption(&puzzle, next, 1, g_check_constr);
    check_result(probe.outcome, 0, 0);
    assert(probe.status == DIVE_PASS);
    assert(memcmp(&before, puzzle.cur_node, sizeof(before)) == 0);
    assert(puzzle.solutions_found == 0);
    puzzle.cur_node->domain.is_invalid = 1;
    probe = probe_assumption(&puzzle, next, 1, g_check_constr);
    check_result(probe.outcome, 0, 1);
    assert(probe.status == DIVE_FAIL);
    puzzle.cur_node->tree.lookahead_depth = MAX_LOOKAHEAD_DEPTH;
    probe = probe_assumption(&puzzle, next, 1, g_check_constr);
    check_result(probe.outcome, 0, 0);
    assert(probe.status == DIVE_SKIP);
    free_solution_storage(&puzzle);
}

int main(void)
{
    test_leaves();
    test_exhaustion_and_limits();
    test_consumption();
    test_restrictions_and_probe();
    return (0);
}
