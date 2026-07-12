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

static const double	g_min_unset_threshold = 0.201176982334429;
static const double	g_gac_min_unset = 0.132431740614728;
static const double	g_constr_min_unset = 0.0255441138829879;
static const double	g_lookahead_downgrade_fraction = 0.0714845042243065;
static const int	g_period_base = 10;
static const int	g_period_coef1 = 2414;
static const int	g_period_coef2 = 30384;
static const double	g_gac_local_min_unset = 0.351998502494427;
static const double	g_gac_local_max_unset = 0.70509433900373;
static const double	g_gac_global_min_unset = 0.495231407740633;
static const double	g_constr_local_min_unset = 0.356143040960021;
static const double	g_constr_local_max_unset = 0.701397240553604;
static const double	g_constr_global_min_unset = 0.505964265587367;
static const double	g_lookahead_gac_local_min_unset = 0.339262188833763;
static const double	g_lookahead_gac_local_max_unset = 0.691937712171258;
static const double	g_lookahead_gac_global_min_unset = 0.502735349801847;
static const double	g_lookahead_constr_local_min_unset = 0.339262188833763;
static const double	g_lookahead_constr_local_max_unset = 0.691937712171258;
static const double	g_lookahead_constr_global_min_unset = 0.502735349801847;

static void	setup_cfg_thresholds(t_prune_routine_cfg *cfg, double unset_ratio)
{
	cfg->run_gac = (unset_ratio >= g_gac_min_unset);
	cfg->run_check_constr = (unset_ratio >= g_constr_min_unset);
	cfg->lookahead.check_mode.run_constr = 1;
	cfg->lookahead.check_mode.run_gac = 1;
	cfg->lookahead.check_mode.run_prop = 1;
	cfg->lookahead.check_mode.downgrade_fraction
		= g_lookahead_downgrade_fraction;
}

static void	setup_cfg_bounds(t_prune_routine_cfg *cfg)
{
	cfg->gac.min_unset = g_gac_local_min_unset;
	cfg->gac.max_unset = g_gac_local_max_unset;
	cfg->gac.global_min_unset = g_gac_global_min_unset;
	cfg->check_constr_min_unset = g_constr_local_min_unset;
	cfg->check_constr_max_unset = g_constr_local_max_unset;
	cfg->check_constr_global_min_unset
		= g_constr_global_min_unset;
	cfg->lookahead.check_mode.constr.min_unset = g_lookahead_constr_local_min_unset;
	cfg->lookahead.check_mode.constr.max_unset = g_lookahead_constr_local_max_unset;
	cfg->lookahead.check_mode.constr.global_min_unset
		= g_lookahead_constr_global_min_unset;
	cfg->lookahead.check_mode.gac.min_unset = g_lookahead_gac_local_min_unset;
	cfg->lookahead.check_mode.gac.max_unset = g_lookahead_gac_local_max_unset;
	cfg->lookahead.check_mode.gac.global_min_unset
		= g_lookahead_gac_global_min_unset;
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
