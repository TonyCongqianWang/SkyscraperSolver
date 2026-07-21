/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   check_node_validity.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/02 23:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/02 23:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "check_node_validity.h"
#include "push_dirty_constraints.h"
#include "constraint_selection.h"
#include "constraint_checking.h"
#include "prune_check_constr.h"
#include "prune_gac.h"

static void	run_gac_analysis(t_puzzle *puzzle, int idx, t_check_mode mode)
{
	t_gac_config	gac_cfg;
	t_node_state	*node;

	node = puzzle->cur_node;
	gac_cfg.selectivity = SELECTIVITY_NONE;
	gac_cfg.max_k = 3;
	gac_cfg.analyse_naked = 1;
	gac_cfg.analyse_hidden = 1;
	gac_cfg.min_unset = mode.gac.min_unset;
	gac_cfg.max_unset = mode.gac.max_unset;
	gac_cfg.global_min_entropy = mode.gac.global_min_entropy;
	analyse_gac_line(puzzle, idx % node->size, idx < node->size,
		&gac_cfg);
}

static void	process_dirty_entry(t_puzzle *puzzle, int entry, t_check_mode mode)
{
	t_node_state	*node;
	int				idx;

	node = puzzle->cur_node;
	idx = entry / 2;
	set_active_constraint(puzzle, idx);
	if (entry % 2)
		reverse_constr_direction(puzzle);
	if (mode.run_constr && !check_active_constr(puzzle))
		node->is_invalid = 1;
	if (node->is_invalid)
		return ;
	if (mode.run_prop)
		process_constraint(puzzle, idx, node->size, &mode.constr);
	if (!node->is_invalid && mode.run_gac)
		run_gac_analysis(puzzle, idx, mode);
}

static int	get_max_high_iters(t_node_state *node, double fraction)
{
	int	max;

	max = (int)(node->num_unset * fraction);
	if (max < 1)
		max = 1;
	return (max);
}

static void	drain_dirty_constraints_mode(t_puzzle *puzzle, t_check_mode mode)
{
	t_dirty_constr_stack	local;
	int						entry;
	int						iter;
	int						max;
	t_check_mode			cur_mode;

	iter = 0;
	max = get_max_high_iters(puzzle->cur_node, mode.downgrade_fraction);
	while (puzzle->cur_node->dirty_constrs.count > 0
		&& !puzzle->cur_node->is_invalid)
	{
		local = puzzle->cur_node->dirty_constrs;
		puzzle->cur_node->dirty_constrs.count = 0;
		puzzle->cur_node->dirty_constrs.in_stack_bmp = 0;
		cur_mode = g_check_constr;
		if (iter < max)
			cur_mode = mode;
		while (local.count > 0 && !puzzle->cur_node->is_invalid)
		{
			entry = local.entries[(int)(--local.count)];
			local.in_stack_bmp &= ~(1ULL << entry);
			process_dirty_entry(puzzle, entry, cur_mode);
		}
		iter++;
	}
}

int	check_node_validity(t_puzzle *puzzle, t_check_mode mode)
{
	drain_dirty_constraints_mode(puzzle, mode);
	return (!puzzle->cur_node->is_invalid);
}
