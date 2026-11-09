#include <assert.h>
#include <string.h>
#include "puzzle_init.h"
#include "grid_interface.h"
#include "search_context.h"
#include "solution_storage.h"
#include "prune_check_constr.h"
#include "prune_gac.h"

static t_solver_state puzzle;
static int propagation_calls, gac_calls, constraint_calls;

int __real_check_active_constr(t_solver_state *solver);
int __wrap_check_active_constr(t_solver_state *solver)
{
    ++constraint_calls;
    return __real_check_active_constr(solver);
}

/* Observe optional analysis without letting it alter the test's branch path. */
int __wrap_process_constraint(t_solver_state *solver, int idx, int size,
                             t_constr_limits *limits)
{
    (void)solver; (void)idx; (void)size; (void)limits;
    ++propagation_calls;
    return 0;
}

void __wrap_analyse_gac_line(t_solver_state *solver, int idx, int is_col,
                            t_gac_config *config)
{
    (void)solver; (void)idx; (void)is_col; (void)config;
    ++gac_calls;
}

static t_node_transition next_value(int cell, int value)
{
    t_node_transition next;
    memset(&next, 0, sizeof(next));
    next.cell_idx = cell;
    next.cell_val = value;
    return next;
}

static t_probe_request reset(int depth)
{
    t_probe_request request;
    memset(&puzzle, 0, sizeof(puzzle));
    assert(init_puzzle(&puzzle, 4, 0));
    puzzle.constraint_pairs[0].fwd_val = 4;
    request.next = next_value(0, 1);
    request.depth = depth;
    request.check_mode = g_check_constr;
    request.check_mode.run_prop = 1;
    request.check_mode.run_gac = 1;
    propagation_calls = 0;
    gac_calls = 0;
    constraint_calls = 0;
    return request;
}

static void assert_checked(int extra)
{
    assert(constraint_calls > 0);
    assert((propagation_calls > 0) == extra);
    assert((gac_calls > 0) == extra);
}

static void test_depth_boundary(void)
{
    t_probe_request request = reset(3);
    t_node_state saved;
    assert(enter_probe(&puzzle, &request, &saved));
    assert_checked(0);
    enter_search_child(&puzzle, next_value(4, 2), 0);
    assert_checked(0);
    enter_search_child(&puzzle, next_value(8, 3), 0);
    assert(puzzle.cur_node->tree.depth == 3);
    assert_checked(1);
    leave_search_child(&puzzle);
    leave_search_child(&puzzle);
    leave_probe(&puzzle, &saved);
    assert(memcmp(&saved, puzzle.cur_node, sizeof(saved)) == 0);
    free_solution_storage(&puzzle);
}

static void test_progress_boundary(void)
{
    t_probe_request request = reset(5);
    t_node_state saved;
    assert(enter_probe(&puzzle, &request, &saved));
    assert_checked(0);
    puzzle.cur_node->search_policy.limits.target_nunset = 14;
    enter_search_child(&puzzle, next_value(4, 2), 0);
    assert(puzzle.cur_node->tree.depth < 5);
    assert(puzzle.cur_node->domain.num_unset <= 14);
    assert_checked(1);
    leave_search_child(&puzzle);
    leave_probe(&puzzle, &saved);
    free_solution_storage(&puzzle);
}

static void test_nested_boundary(void)
{
    t_probe_request request = reset(3);
    t_node_state outer, inner;
    assert(enter_probe(&puzzle, &request, &outer));
    request.next = next_value(4, 2);
    request.depth = 1;
    assert(enter_probe(&puzzle, &request, &inner));
    assert(puzzle.cur_node->tree.lookahead_depth == 2);
    assert(puzzle.cur_node->tree.depth == puzzle.cur_node->search_policy.limits.max_depth);
    assert_checked(0);
    leave_probe(&puzzle, &inner);
    assert(memcmp(&inner, puzzle.cur_node, sizeof(inner)) == 0);
    /* Restoring the outer probe must also restore its leaf checking mode. */
    enter_search_child(&puzzle, next_value(4, 2), 0);
    enter_search_child(&puzzle, next_value(8, 3), 0);
    assert_checked(1);
    leave_search_child(&puzzle);
    leave_search_child(&puzzle);
    leave_probe(&puzzle, &outer);
    free_solution_storage(&puzzle);
}

static void test_depth_one_and_ordinary_checks(void)
{
    t_probe_request request = reset(1);
    t_node_state saved;
    assert(enter_probe(&puzzle, &request, &saved));
    assert_checked(1);
    leave_probe(&puzzle, &saved);
    free_solution_storage(&puzzle);
    request = reset(3);
    set_cell_val(&puzzle, 0, 1, request.check_mode);
    assert_checked(1);
    free_solution_storage(&puzzle);
}

int main(void)
{
    test_depth_boundary();
    test_progress_boundary();
    test_nested_boundary();
    test_depth_one_and_ordinary_checks();
    return 0;
}
