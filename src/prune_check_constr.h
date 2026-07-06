/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_check_constr.h                               :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */
#ifndef PRUNE_CHECK_CONSTR_H
# define PRUNE_CHECK_CONSTR_H

# include "puzzle_structs.h"
# include "strategy_config.h"

typedef struct s_dp_tables
{
	char	pref_max[MAX_SIZE + 1][MAX_SIZE + 1];
	char	pref_min[MAX_SIZE + 1][MAX_SIZE + 1];
	char	suff_max[MAX_SIZE + 1][MAX_SIZE + 1];
	char	suff_min[MAX_SIZE + 1][MAX_SIZE + 1];
}	t_dp_tables;

typedef struct s_prune_args
{
	t_puzzle		*puzzle;
	t_node_state	*state;
	t_dp_tables		*dp;
	int				*grid_indices;
	int				size;
	int				target_clue;
}	t_prune_args;

void	prune_check_constr(t_puzzle *puzzle, t_selectivity_level selectivity);
void	init_dp_tables(t_dp_tables *dp, int size);
void	fill_pref_dp(t_dp_tables *dp, int *cell_domains, int size);
void	fill_suff_dp(t_dp_tables *dp, int *cell_domains, int size);
int		collect_domains(t_node_state *state, int *grid_indices,
			int size, int *cell_domains);
int		prune_candidates(t_prune_args *args);
int		propagate_single_direction(t_prune_args *args);
void	copy_indices(t_puzzle *puzzle, int *grid, int *rev, int size);

#endif
