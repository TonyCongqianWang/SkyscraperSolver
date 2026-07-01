/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_shallow.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_strat_shallow.h"
#include "pruning_routines.h"

static const double	g_min_unset_threshold = 0.468567996202653;
static const double	g_gac_unset_threshold = 0.128731975177545;
static const double	g_constr_min_unset = 0.445357456976812;
static const double	g_constr_max_unset = 0.809890431611463;
static const int	g_period_base = 6;
static const int	g_period_coef1 = 2464;
static const int	g_period_coef2 = 21788;

static int	run_tier(t_puzzle *puzzle, int tier, double unset_ratio)
{
	t_prune_routine_cfg	cfg;

	if (tier == 0)
		get_prune_cfg_light(&cfg);
	else if (tier == 1)
		get_prune_cfg_medium(&cfg);
	else
		get_prune_cfg_heavy(&cfg);
	cfg.run_gac = (unset_ratio >= g_gac_unset_threshold);
	cfg.run_check_constr = (unset_ratio >= g_constr_min_unset
			&& unset_ratio <= g_constr_max_unset);
	return (run_pruning_routine(puzzle, &cfg, tier));
}

int	prune_strat_shallow(t_puzzle *puzzle)
{
	t_node_state	*node;
	double			unset_ratio;
	double			x;
	t_prune_prog	period;

	node = puzzle->cur_node;
	if (node->is_invalid || node->is_complete || node->num_unset == 0)
		return (0);
	unset_ratio = (double)node->num_unset / puzzle->squared_size;
	if (unset_ratio < g_min_unset_threshold)
		return (0);
	x = 1 - unset_ratio;
	period = (t_prune_prog)(g_period_base + g_period_coef1 * x * x
			+ g_period_coef2 * x * x * x * x);
	if (node->progress_counter > node->last_prog[0] + period / 2)
		return (run_tier(puzzle, 0, unset_ratio));
	if (node->progress_counter > node->last_prog[1] + period)
		return (run_tier(puzzle, 1, unset_ratio));
	if (node->progress_counter > node->last_prog[2] + period * 2)
		return (run_tier(puzzle, 2, unset_ratio));
	return (0);
}
