#include "puzzle_init.h"
#include "puzzle_solver.h"
#include "solution_storage.h"
#include "string_interface.h"
#include <assert.h>
#include <stdlib.h>
#include <string.h>

static void	check_initialized(t_puzzle *puzzle, int size)
{
	int	idx;

	assert(puzzle->cur_node == &puzzle->node_stack[0]);
	assert(puzzle->cur_node->puzzle == puzzle);
	assert(puzzle->cur_node->dirty_constrs.count == 0);
	assert(puzzle->cur_node->dirty_constrs.in_stack_bmp == 0);
	assert(puzzle->cur_node->lookahead_ctx == NULL);
	assert(puzzle->cur_node->is_in_neg_lookahead == 0);
	assert(puzzle->cur_node->search_policy.branch.is_in_lookahead_select == 0);
	assert(puzzle->cur_node->search_policy.branch.lookahead_selectivity == SELECTIVITY_NONE);
	assert(puzzle->order_stack.top_idx == 0);
	assert(puzzle->order_stack.orders[0].count == 0);
		idx = 0;
	while (idx < 2 * size)
	{
		assert(puzzle->constraint_pairs[idx].fwd_val == 0);
		assert(puzzle->constraint_pairs[idx].bwd_val == 0);
		idx++;
	}
}

int	main(void)
{
	t_puzzle	*puzzle;
	char		clues[] = "1 3 3 0 0 0 0 2 0 0 0 0 0 0 0 0";
	char		grid[] = "1 2 3 4 2 3 4 1 3 4 1 2 4 1 2 3";

	puzzle = malloc(sizeof(*puzzle));
	assert(puzzle != NULL);
	memset(puzzle, 0xa5, sizeof(*puzzle));
	init_puzzle(puzzle, 4, 1);
	check_initialized(puzzle, 4);
	assert(set_puzzle_grid_to_str_vals(puzzle, grid));
	assert(puzzle->cur_node->grid.vals[0] == 1);
	assert(puzzle->cur_node->grid.vals[15] == 3);
	free_solution_storage(puzzle);
	init_puzzle(puzzle, 4, 1);
	check_initialized(puzzle, 4);
	free_solution_storage(puzzle);
	memset(puzzle, 0xa5, sizeof(*puzzle));
	assert(init_puzzle_from_constr_str(puzzle, clues, NULL));
	assert(puzzle->constraint_pairs[0].fwd_val == 1);
	assert(puzzle->constraint_pairs[0].bwd_val == 0);
	assert(solve_puzzle(puzzle, -1) == 1);
	free_solution_storage(puzzle);
	free(puzzle);
	return (0);
}
