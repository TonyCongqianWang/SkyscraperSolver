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
#include "math_utils.h"
#include <math.h>

static const int		g_min_entropy_threshold = 199326;
static const int		g_gac_min_entropy = 237564;
static const int		g_constr_min_entropy = 529983;
static const double		g_lookahead_downgrade_fraction = 0.110960656995948;
static const long long	g_period_scale = 1000000;
static const double		g_period_coef_sqrt = 17;
static const double		g_period_coef_inv = 4;
static const double		g_period_coef_unset = 7;
static const double		g_gac_local_min_unset = 0.271263956380736;
static const double		g_gac_local_max_unset = 0.863263356194274;
static const int		g_gac_global_min_entropy = 501367;
static const double		g_constr_local_min_unset = 0.251980023750893;
static const double		g_constr_local_max_unset = 0.881244610981394;
static const int		g_constr_global_min_entropy = 440965;
static const double		g_lookahead_gac_local_min_unset = 0.250843378588605;
static const double		g_lookahead_gac_local_max_unset = 0.868546773931959;
static const int		g_lookahead_gac_global_min_entropy = 432645;
static const double		g_lookahead_constr_local_min_unset = 0.253669612693451;
static const double		g_lookahead_constr_local_max_unset = 0.865753222826758;
static const int		g_lookahead_constr_global_min_entropy = 529885;

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
	double			raw;
	double			period;
	int				rem;

	node = puzzle->cur_node;
	if (node->is_invalid || node->is_complete || node->num_unset == 0)
		return (0);
	if (node->remaining_entropy < g_min_entropy_threshold)
		return (0);
	rem = node->remaining_entropy;
	if (rem < 1)
		rem = 1;
	raw = (double)(puzzle->max_entropy - rem)
		* g_period_scale / rem;
	period = g_period_coef_sqrt * sqrt(raw)
		+ g_period_coef_inv * (raw / 1000.0)
		+ g_period_coef_unset * (puzzle->squared_size - node->num_unset);
	if (node->last_entropy[0] - node->remaining_entropy > period / 2)
		return (run_tier(puzzle, 0, node->remaining_entropy));
	if (node->last_entropy[1] - node->remaining_entropy > period)
		return (run_tier(puzzle, 1, node->remaining_entropy));
	if (node->last_entropy[2] - node->remaining_entropy > period * 2)
		return (run_tier(puzzle, 2, node->remaining_entropy));
	return (0);
}
