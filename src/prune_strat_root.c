/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_root.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_strat_root.h"
#include "pruning_routines.h"

static const double	g_min_unset_threshold = 0.2;
static const double	g_gac_unset_threshold = 0.133056682040898;
static const double	g_constr_min_unset = 0.0355884363571201;
static const double	g_lookahead_gac_unset_threshold = 0.151932027085723;
static const double	g_lookahead_constr_min_unset = 0.0291882141965284;
static const double	g_lookahead_downgrade_fraction = 0.0727673746639766;
static const int	g_period_base = 8;
static const int	g_period_coef1 = 2352;
static const int	g_period_coef2 = 28972;
static const double	g_gac_local_min_unset = 0.35;
static const double	g_gac_local_max_unset = 0.70;
static const double	g_gac_local_global_min_unset = 0.50;
static const double	g_constr_local_min_unset = 0.35;
static const double	g_constr_local_max_unset = 0.70;
static const double	g_constr_local_global_min_unset = 0.50;
static const double	g_lookahead_local_min_unset = 0.35;
static const double	g_lookahead_local_max_unset = 0.70;
static const double	g_lookahead_local_global_min_unset = 0.50;

static void	setup_cfg_thresholds(t_prune_routine_cfg *cfg, double unset_ratio)
{
	cfg->run_gac = (unset_ratio >= g_gac_unset_threshold);
	cfg->run_check_constr = (unset_ratio >= g_constr_min_unset);
	cfg->lookahead.check_mode.run_constr = 1;
	cfg->lookahead.check_mode.run_gac = (unset_ratio
			>= g_lookahead_gac_unset_threshold);
	cfg->lookahead.check_mode.run_prop = (unset_ratio
			>= g_lookahead_constr_min_unset);
	cfg->lookahead.check_mode.downgrade_fraction
		= g_lookahead_downgrade_fraction;
}

static void	setup_cfg_bounds(t_prune_routine_cfg *cfg)
{
	cfg->gac.min_unset = g_gac_local_min_unset;
	cfg->gac.max_unset = g_gac_local_max_unset;
	cfg->gac.global_min_unset = g_gac_local_global_min_unset;
	cfg->check_constr_min_unset = g_constr_local_min_unset;
	cfg->check_constr_max_unset = g_constr_local_max_unset;
	cfg->check_constr_global_min_unset
		= g_constr_local_global_min_unset;
	cfg->lookahead.check_mode.min_unset = g_lookahead_local_min_unset;
	cfg->lookahead.check_mode.max_unset = g_lookahead_local_max_unset;
	cfg->lookahead.check_mode.global_min_unset
		= g_lookahead_local_global_min_unset;
}

static int	run_tier(t_puzzle *puzzle, int tier, double unset_ratio)
{
	t_prune_routine_cfg	cfg;

	if (tier == 0)
		get_prune_cfg_light(&cfg);
	else if (tier == 1)
		get_prune_cfg_medium(&cfg);
	else
		get_prune_cfg_heavy(&cfg);
	setup_cfg_thresholds(&cfg, unset_ratio);
	setup_cfg_bounds(&cfg);
	return (run_pruning_routine(puzzle, &cfg, tier));
}

int	prune_strat_root(t_puzzle *puzzle)
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
