/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   prune_strat_deep.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/18 16:17:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 13:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "prune_strat_deep.h"
#include "pruning_routines.h"
#include "entropy.h"

static const int	g_min_entropy_threshold = 183314;
static const int	g_gac_min_entropy = 248894;
static const int	g_constr_min_entropy = 553039;
static const double	g_lookahead_downgrade_fraction = 0.0926045184018191;
static const long long	g_period_scale = 1000000;
static const int	g_period_coef_sqrt = 17;
static const int	g_period_coef_inv = 4;
static const int	g_period_coef_unset = 4;
static const double	g_gac_local_min_unset = 0.266661339259724;
static const double	g_gac_local_max_unset = 0.868711152093341;
static const int	g_gac_global_min_entropy = 487465;
static const double	g_constr_local_min_unset = 0.252073368050884;
static const double	g_constr_local_max_unset = 0.877144826285916;
static const int	g_constr_global_min_entropy = 458252;
static const double	g_lookahead_gac_local_min_unset = 0.244984853085172;
static const double	g_lookahead_gac_local_max_unset = 0.871691056569888;
static const int	g_lookahead_gac_global_min_entropy = 422238;
static const double	g_lookahead_constr_local_min_unset = 0.244327803858185;
static const double	g_lookahead_constr_local_max_unset = 0.869366448077845;
static const int	g_lookahead_constr_global_min_entropy = 533204;

static void	setup_cfg_thresholds(t_prune_routine_cfg *cfg,
		int remaining_entropy)
{
	cfg->run_gac = (remaining_entropy >= g_gac_min_entropy);
	cfg->run_check_constr = (remaining_entropy >= g_constr_min_entropy);
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
	cfg->gac.global_min_entropy = g_gac_global_min_entropy;
	cfg->check_constr_min_unset = g_constr_local_min_unset;
	cfg->check_constr_max_unset = g_constr_local_max_unset;
	cfg->check_constr_global_min_entropy
		= g_constr_global_min_entropy;
	cfg->lookahead.check_mode.constr.min_unset
		= g_lookahead_constr_local_min_unset;
	cfg->lookahead.check_mode.constr.max_unset
		= g_lookahead_constr_local_max_unset;
	cfg->lookahead.check_mode.constr.global_min_entropy
		= g_lookahead_constr_global_min_entropy;
	cfg->lookahead.check_mode.gac.min_unset
		= g_lookahead_gac_local_min_unset;
	cfg->lookahead.check_mode.gac.max_unset
		= g_lookahead_gac_local_max_unset;
	cfg->lookahead.check_mode.gac.global_min_entropy
		= g_lookahead_gac_global_min_entropy;
}

static int	run_tier(t_puzzle *puzzle, int tier, int remaining_entropy)
{
	t_prune_routine_cfg	cfg;

	if (tier == 0)
		get_prune_cfg_light(&cfg);
	else if (tier == 1)
		get_prune_cfg_medium(&cfg);
	else
		get_prune_cfg_heavy(&cfg);
	setup_cfg_thresholds(&cfg, remaining_entropy);
	setup_cfg_bounds(&cfg);
	return (run_pruning_routine(puzzle, &cfg, tier));
}

int	prune_strat_deep(t_puzzle *puzzle)
{
	t_node_state	*node;
	long long		raw;
	int				rem;
	int				period;

	node = puzzle->cur_node;
	if (node->is_invalid || node->is_complete || node->num_unset == 0)
		return (0);
	if (node->remaining_entropy < g_min_entropy_threshold)
		return (0);
	rem = node->remaining_entropy;
	if (rem < 1)
		rem = 1;
	raw = (long long)(puzzle->max_entropy - rem)
		* g_period_scale / rem;
	period = g_period_coef_sqrt * isqrt_approx(raw)
		+ g_period_coef_inv * (int)(raw / 1000)
		+ g_period_coef_unset * (puzzle->squared_size - node->num_unset);
	if (node->last_entropy[0] - node->remaining_entropy > period / 2)
		return (run_tier(puzzle, 0, node->remaining_entropy));
	if (node->last_entropy[1] - node->remaining_entropy > period)
		return (run_tier(puzzle, 1, node->remaining_entropy));
	if (node->last_entropy[2] - node->remaining_entropy > period * 2)
		return (run_tier(puzzle, 2, node->remaining_entropy));
	return (0);
}
