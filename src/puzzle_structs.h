/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   puzzle_structs.h                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/30 19:47:55 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PUZZLE_STRUCTS_H
# define PUZZLE_STRUCTS_H
# define MAX_N_CONSTR_PAIRS 18
# define MAX_CELL_COUNT 81
# define MAX_SIZE 9
# define C_PAIRS_PER_CELL 2

typedef struct s_puzzle	t_puzzle;

typedef struct s_node_transition
{
	int			cell_idx;
	char		cell_val;
	int			num_valids_col;
	int			num_valids_row;
	int			num_valids_cell;
	double		score;
}		t_node_transition;

typedef struct s_grid_state
{
	char		vals[MAX_CELL_COUNT];
	short		valid_val_bmps[MAX_CELL_COUNT];
	char		cell_bounds[MAX_CELL_COUNT];
	char		num_cell_vals[MAX_CELL_COUNT];
}		t_grid_state;

typedef struct s_constrs_state
{
	char		num_val_positions[MAX_N_CONSTR_PAIRS][MAX_SIZE];
}		t_constrs_state;

typedef struct s_node_state
{
	t_puzzle			*puzzle;
	int					size;
	int					last_prune_nunset;
	int					cur_prune_nunset;
	int					cur_depth;
	int					max_depth;
	int					last_set_idx;
	int					is_complete;
	int					is_invalid;
	int					sub_node_depth;
	int					num_unset;
	t_grid_state		grid;
	t_constrs_state		constrs;
}		t_node_state;

typedef struct s_constraint_pair
{
	int				fwd_val;
	int				bwd_val;
	int				grid_indeces[MAX_SIZE];
}		t_constraint_pair;

typedef struct s_constraint_bounds
{
	int					size;
	t_constraint_pair	cur_c_pair;
	int					is_reverse;
	int					fwd_lb;
	int					lhs_ub;
	int					max_height_lb;
	int					max_height_ub;
}		t_constraint_bounds;

typedef struct s_node_pruning_state
{
	int		can_reiterate;
	int		last_iteration_succeeded;
	int		cur_pruning_depth;
	int		max_pruning_depth;
}		t_node_pruning_state;

typedef struct s_puzzle
{
	int						size;
	unsigned long long		max_solutions;
	unsigned long long		solutions_found;
	unsigned long long		nodes_visited;
	t_constraint_pair		constraint_pairs[MAX_N_CONSTR_PAIRS];
	int						grid_constr_map[MAX_CELL_COUNT][C_PAIRS_PER_CELL];
	t_node_state			stored_node;
	t_node_state			*cur_node;
	t_node_state			*solutions;
	t_constraint_bounds		constr_bounds;
	t_node_pruning_state	pruning;
}		t_puzzle;

#endif
