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
#include "pruning_configs.h"
#include "entropy.h"
#include "math_utils.h"

static const int		g_min_entropy_threshold = 100000;
static const int		g_gac_min_entropy = 186908;
static const int		g_constr_min_entropy = 393682;
static const double		g_lookahead_downgrade_fraction = 0.009;
static const double		g_period_coef_sqrt = 48.55271996020715;
static const double		g_period_coef_inv = 25.55038003454135;
static const double		g_period_coef_unset = 1.68236572579932;
static const double		g_period_tier_medium_mult = 2.0;
static const double		g_period_tier_heavy_mult = 4.0;
static const double		g_gac_local_min_unset = 0.260199037090635;
static const double		g_gac_local_max_unset = 0.865914267598487;
static const int		g_gac_global_min_entropy = 620755;
static const double		g_constr_local_min_unset = 0.266574406617534;
static const double		g_constr_local_max_unset = 0.907770085809651;
static const int		g_constr_global_min_entropy = 478679;
static const double		g_lookahead_gac_local_min_unset = 0.234407619210545;
static const double		g_lookahead_gac_local_max_unset = 0.856291502297538;
static const int		g_lookahead_gac_global_min_entropy = 708202;
static const double		g_lookahead_constr_local_min_unset = 0.294386521174934;
static const double		g_lookahead_constr_local_max_unset = 0.905650426335935;
static const int		g_lookahead_constr_global_min_entropy = 427261;

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

int	prune_strat_shallow(t_puzzle *puzzle)
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
