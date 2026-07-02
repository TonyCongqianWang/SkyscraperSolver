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
# include "strategy_config.h"

# define MAX_N_CONSTR_PAIRS 18
# define MAX_CELL_COUNT 81
# define MAX_SIZE 9
# define C_PAIRS_PER_CELL 2
# define MAX_DIRTY_CONSTRS (MAX_N_CONSTR_PAIRS * 2)

typedef unsigned short		t_u16;
typedef unsigned long long	t_u64;
typedef t_u64				t_prune_prog;
typedef t_u64				t_sol_count;
typedef t_u64				t_node_count;
typedef struct s_puzzle		t_puzzle;

typedef struct s_node_transition
{
	int			cell_idx;
	char		cell_val;
	int			num_valids_col;
	int			num_valids_row;
	int			num_valids_cell;
	double		score;
}		t_node_transition;

typedef struct s_node_order
{
	t_node_transition	entries[MAX_CELL_COUNT];
	int					count;
	t_prune_prog		last_build_prog;
	int					build_depth;
}		t_node_order;

# define MAX_STACK_DEPTH 128

typedef struct s_node_orders_stack
{
	t_node_order	orders[MAX_STACK_DEPTH];
	int				top_idx;
}		t_node_orders_stack;

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

typedef struct s_dirty_constr_stack
{
	char	entries[MAX_DIRTY_CONSTRS];
	char	count;
	t_u64	in_stack_bmp;
}		t_dirty_constr_stack;

typedef struct s_lookahead_ctx
{
	int						curr_pass;
	int						curr_index;
	char					cell_passes[MAX_CELL_COUNT];
}		t_lookahead_ctx;

typedef struct s_node_state
{
	int						size;
	int						last_prune_nunset;
	int						cur_depth;
	int						max_depth;
	int						last_set_idx;
	int						is_complete;
	int						is_invalid;
	int						sub_node_depth;
	int						target_nunset;
	int						num_unset;
	t_u16					rows_changed_since_prune;
	t_u16					cols_changed_since_prune;
	t_u16					rows_invalid_since_prune;
	t_u16					cols_invalid_since_prune;
	int						is_in_lookahead_select;
	t_selectivity_level		lookahead_selectivity;
	double					lookahead_scores[MAX_CELL_COUNT][MAX_SIZE + 1];
	t_node_order			*order_cache;
	t_lookahead_ctx			*lookahead_ctx;
	int						lowest_empty_idx;
	t_prune_prog			progress_counter;
	t_prune_prog			last_prog[4];
	t_sol_count				max_solutions;
	t_sol_count				solutions_found;
	t_grid_state			grid;
	t_constrs_state			constrs;
	t_dirty_constr_stack	dirty_constrs;
	t_puzzle				*puzzle;
}		t_node_state;

typedef struct s_sol_info
{
	int						min_nunset;
	t_sol_count				solutions_found;
}		t_sol_info;

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
	int						squared_size;
	t_sol_count				max_solutions;
	t_sol_count				solutions_found;
	t_node_count			nodes_visited;
	t_node_count			main_nodes_visited;
	int						prune_runs_count;
	t_constraint_pair		constraint_pairs[MAX_N_CONSTR_PAIRS];
	int						grid_constr_map[MAX_CELL_COUNT][C_PAIRS_PER_CELL];
	t_node_state			sol_node_storage;
	t_node_state			*cur_node;
	t_node_state			*solutions;
	t_constraint_bounds		constr_bounds;
	t_node_orders_stack		order_stack;
	t_node_state			node_stack[MAX_STACK_DEPTH];
	int						node_stack_top;
}		t_puzzle;

#endif
