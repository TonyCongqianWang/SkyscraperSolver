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
#include "pruning_configs.h"
#include "entropy.h"
#include "math_utils.h"

static const int		g_min_entropy_threshold = 246577;
static const int		g_gac_min_entropy = 261334;
static const int		g_constr_min_entropy = 514370;
static const double		g_lookahead_downgrade_fraction = 0.120374788066341;
static const double		g_period_coef_sqrt = 1083.52198515116;
static const double		g_period_coef_inv = 2012.79885806126;
static const double		g_period_coef_unset = 2.95695576127101;
static const double		g_period_tier_medium_mult = 2.05736212682385;
static const double		g_period_tier_heavy_mult = 3.48465986993358;
static const double		g_gac_local_min_entropy = 0.282318334670467;
static const double		g_gac_local_max_entropy = 0.85771945194264;
static const int		g_gac_global_min_entropy = 533732;
static const double		g_constr_local_min_entropy = 0.27193613514193;
static const double		g_constr_local_max_entropy = 0.876915319543804;
static const int		g_constr_global_min_entropy = 453122;
static const double		g_lookahead_gac_local_min_entropy = 0.24345386;
static const double		g_lookahead_gac_local_max_entropy = 0.88486337;
static const int		g_lookahead_gac_global_min_entropy = 431435;
static const double		g_lookahead_constr_local_min_entropy = 0.26657803;
static const double		g_lookahead_constr_local_max_entropy = 0.84830541;
static const int		g_lookahead_constr_global_min_entropy = 498503;

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
	cfg->gac.min_entropy = g_gac_local_min_entropy;
	cfg->gac.max_entropy = g_gac_local_max_entropy;
	cfg->gac.global_min_entropy = g_gac_global_min_entropy;
	cfg->check_constr_min_entropy = g_constr_local_min_entropy;
	cfg->check_constr_max_entropy = g_constr_local_max_entropy;
	cfg->check_constr_global_min_entropy
		= g_constr_global_min_entropy;
	cfg->lookahead.check_mode.constr.min_entropy
		= g_lookahead_constr_local_min_entropy;
	cfg->lookahead.check_mode.constr.max_entropy
		= g_lookahead_constr_local_max_entropy;
	cfg->lookahead.check_mode.constr.global_min_entropy
		= g_lookahead_constr_global_min_entropy;
	cfg->lookahead.check_mode.gac.min_entropy
		= g_lookahead_gac_local_min_entropy;
	cfg->lookahead.check_mode.gac.max_entropy
		= g_lookahead_gac_local_max_entropy;
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
	double			raw;
	double			period;
	int				rem;

	node = puzzle->cur_node;
	if (node->is_invalid || node->is_complete || node->num_unset == 0
		|| node->remaining_entropy < g_min_entropy_threshold)
		return (0);
	rem = node->remaining_entropy;
	if (rem < 1)
		rem = 1;
	raw = (double)(puzzle->max_entropy - rem) / rem;
	period = g_period_coef_sqrt * dsqrt_approx(raw)
		+ g_period_coef_inv * raw
		+ g_period_coef_unset * (puzzle->squared_size - node->num_unset);
	if (node->last_entropy[0] - node->remaining_entropy > period)
		return (run_tier(puzzle, 0, node->remaining_entropy));
	if (node->last_entropy[1] - node->remaining_entropy
		> period * g_period_tier_medium_mult)
		return (run_tier(puzzle, 1, node->remaining_entropy));
	if (node->last_entropy[2] - node->remaining_entropy
		> period * g_period_tier_heavy_mult)
		return (run_tier(puzzle, 2, node->remaining_entropy));
	return (0);
}
