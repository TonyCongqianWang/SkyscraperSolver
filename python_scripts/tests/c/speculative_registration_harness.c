#include <assert.h>
#include <string.h>
#include "puzzle_init.h"
#include "puzzle_solver.h"
#include "tree_search.h"
#include "search_context.h"
#include "search_result.h"
#include "solution_info.h"
#include "solution_storage.h"
#include "lookahead_dive.h"

static t_solver_state puzzle;

static void reset(int size, int limit)
{
    memset(&puzzle, 0, sizeof(puzzle));
    assert(init_puzzle(&puzzle, size, limit));
}

static t_node_transition next_value(int cell, int value)
{
    t_node_transition next;
    memset(&next, 0, sizeof(next));
    next.cell_idx = cell;
    next.cell_val = value;
    return next;
}

static void check_grid(const t_node_state *node)
{
    int row, col, i, rows, cols;
    int size = node->size;
    assert(node->domain.is_complete && !node->domain.is_invalid);
    for (i = 0; i < size; ++i)
    {
        rows = 0;
        cols = 0;
        for (row = 0; row < size; ++row)
        {
            int v = node->domain.vals[i * size + row];
            assert(v >= 1 && v <= size);
            rows |= 1 << (v - 1);
        }
        for (col = 0; col < size; ++col)
        {
            int v = node->domain.vals[col * size + i];
            assert(v >= 1 && v <= size);
            cols |= 1 << (v - 1);
        }
        assert(rows == (1 << size) - 1 && cols == (1 << size) - 1);
    }
}

static void fill_latin(void)
{
    int i;
    for (i = 0; i < puzzle.squared_size; ++i)
    {
        int value = (i / puzzle.size + i % puzzle.size) % puzzle.size + 1;
        if (puzzle.cur_node->domain.vals[i] == 0)
            set_cell_val(&puzzle, i, value, g_check_none);
        assert(puzzle.cur_node->domain.vals[i] == value);
    }
    check_grid(puzzle.cur_node);
}

static void test_forced_completion(int negative)
{
    t_probe_result probe;
    t_node_state saved;
    t_result_transition transition;
    t_sol_info aggregate, rest;

    reset(2, 3);
    saved = *puzzle.cur_node;
    transition.next = next_value(0, 1);
    transition.is_neg = negative;
    if (negative)
        probe = probe_exclusion(&puzzle, transition.next, 1, g_check_constr);
    else
        probe = probe_assumption(&puzzle, transition.next, 1, g_check_constr);
    assert(probe.status == DIVE_PASS);
    assert(probe.outcome.solutions_registered == 1 && probe.outcome.exhausted);
    assert(puzzle.solutions_found == 1 && !puzzle.provisional_solution);
    assert(memcmp(&saved, puzzle.cur_node, sizeof(saved)) == 0);
    check_grid(&puzzle.solutions[0]);
    assert(puzzle.solutions[0].tree.depth == 1);
    assert(puzzle.solutions[0].tree.unbounded_depth == 0);
    init_sol_info(&aggregate, 1, 0);
    consume_child_result(&puzzle, &transition, &probe.outcome, &aggregate);
    assert(aggregate.solutions_registered == 1);
    rest = tree_search(&puzzle);
    assert(rest.solutions_registered == 1 && rest.exhausted);
    assert(puzzle.solutions_found == 2);
    check_grid(&puzzle.solutions[1]);
    assert(memcmp(puzzle.solutions[0].domain.vals,
                  puzzle.solutions[1].domain.vals, 4) != 0);
    free_solution_storage(&puzzle);
}

static void test_disallowed_and_provisional_leaf(void)
{
    t_sol_info result;
    int limit;
    for (limit = 0; limit <= 2; ++limit)
    {
        reset(4, limit);
        puzzle.cur_node->tree.depth = 3;
        puzzle.cur_node->tree.unbounded_depth = 0;
        puzzle.cur_node->tree.lookahead_depth = 2;
        fill_latin();
        result = handle_leaf_node(&puzzle);
        assert(!result.exhausted);
        assert(result.solutions_registered == (limit == 1));
        assert(puzzle.solutions_found == (t_sol_count)(limit == 1));
        assert(puzzle.provisional_solution == (limit == 1));
        rollback_provisional_solution(&puzzle);
        rollback_provisional_solution(&puzzle);
        assert(puzzle.solutions_found == 0 && !puzzle.provisional_solution);
        free_solution_storage(&puzzle);
    }
}

static void test_unbounded_prefix(void)
{
    t_probe_request request;
    t_node_state saved;
    reset(4, 0);
    assert(puzzle.cur_node->tree.unbounded_depth == 0);
    enter_search_child(&puzzle, next_value(0, 1), 0);
    assert(puzzle.cur_node->tree.depth == 1);
    assert(puzzle.cur_node->tree.unbounded_depth == 1);
    request.next = next_value(1, 2);
    request.depth = 3;
    request.check_mode = g_check_constr;
    assert(enter_probe(&puzzle, &request, &saved));
    assert(puzzle.cur_node->tree.depth == 2);
    assert(puzzle.cur_node->tree.unbounded_depth == 1);
    enter_search_child(&puzzle, next_value(2, 3), 0);
    assert(puzzle.cur_node->tree.depth == 3);
    assert(puzzle.cur_node->tree.unbounded_depth == 1);
    leave_search_child(&puzzle);
    leave_probe(&puzzle, &saved);
    assert(memcmp(&saved, puzzle.cur_node, sizeof(saved)) == 0);
    leave_search_child(&puzzle);
    assert(puzzle.cur_node->tree.unbounded_depth == 0);
    free_solution_storage(&puzzle);
}

static void test_automatic_rollback_on_resume(void)
{
    t_probe_result probe;
    t_sol_info result;
    t_node_state before;
    t_node_count visited;

    reset(4, 1);
    before = *puzzle.cur_node;
    probe = probe_assumption(&puzzle, next_value(0, 1), 16, g_check_constr);
    assert(probe.outcome.solutions_registered == 1 && !probe.outcome.exhausted);
    assert(puzzle.solutions_found == 1 && puzzle.provisional_solution);
    assert(memcmp(&before, puzzle.cur_node, sizeof(before)) == 0);
    check_grid(&puzzle.solutions[0]);
    assert(puzzle.solutions[0].tree.depth > 1);
    visited = puzzle.nodes_visited;
    /* A continuation must replace the retracted slot, not reuse stale storage. */
    puzzle.solutions[0].domain.vals[0] = 0;
    result = tree_search(&puzzle);
    assert(result.solutions_registered == 1 && !result.exhausted);
    assert(puzzle.solutions_found == 1 && puzzle.nodes_visited > visited);
    check_grid(&puzzle.solutions[0]);
    free_solution_storage(&puzzle);
}

static void test_only_last_slot_is_retracted(void)
{
    t_node_state empty, committed;
    t_probe_result probe;
    t_sol_info result;

    reset(4, 2);
    empty = *puzzle.cur_node;
    fill_latin();
    result = handle_leaf_node(&puzzle);
    assert(result.solutions_registered == 1 && result.exhausted);
    committed = puzzle.solutions[0];
    *puzzle.cur_node = empty;
    probe = probe_assumption(&puzzle, next_value(0, 2), 16, g_check_constr);
    assert(probe.outcome.solutions_registered == 1 && !probe.outcome.exhausted);
    assert(puzzle.solutions_found == 2 && puzzle.provisional_solution);
    assert(puzzle.solutions[1].domain.vals[0] == 2);
    probe = probe_assumption(&puzzle, next_value(0, 3), 16, g_check_constr);
    assert(probe.outcome.solutions_registered == 1 && !probe.outcome.exhausted);
    assert(puzzle.solutions_found == 2 && puzzle.provisional_solution);
    assert(puzzle.solutions[1].domain.vals[0] == 3);
    assert(memcmp(&committed, &puzzle.solutions[0], sizeof(committed)) == 0);
    check_grid(&puzzle.solutions[1]);
    rollback_provisional_solution(&puzzle);
    assert(puzzle.solutions_found == 1 && !puzzle.provisional_solution);
    free_solution_storage(&puzzle);
}

static void test_unique_storage(int limit)
{
    t_sol_count i, j;
    int expected = limit < 576 ? limit : 576;
    reset(4, limit);
    assert(solve_puzzle(&puzzle, -1) == expected);
    assert(puzzle.solutions_found == (t_sol_count)expected);
    if (limit > 576)
        assert(!puzzle.provisional_solution);
    for (i = 0; i < puzzle.solutions_found; ++i)
    {
        check_grid(&puzzle.solutions[i]);
        for (j = 0; j < i; ++j)
            assert(memcmp(puzzle.solutions[i].domain.vals,
                          puzzle.solutions[j].domain.vals, 16) != 0);
    }
    free_solution_storage(&puzzle);
}

int main(void)
{
    test_forced_completion(0);
    test_forced_completion(1);
    test_disallowed_and_provisional_leaf();
    test_unbounded_prefix();
    test_automatic_rollback_on_resume();
    test_only_last_slot_is_retracted();
    test_unique_storage(1);
    test_unique_storage(2);
    test_unique_storage(10);
    test_unique_storage(575);
    test_unique_storage(576);
    test_unique_storage(600);
    return (0);
}
