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

#include <stdlib.h>

static double	g_gac_unset_threshold = 0.4634853676455628;
static double	g_constr_min_unset = 0.820455247534949;
static double	g_constr_max_unset = 0.33143801544130486;
static int		g_period_base = 70;
static int		g_period_coef1 = 1855;
static int		g_period_coef2 = 109817;

#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
static void	init_env(void)
{
	static int	initialized = 0;
	char		*val;

	if (initialized)
		return ;
	val = getenv("ROOT_GAC_UNSET_THRESHOLD");
	if (val)
		g_gac_unset_threshold = atof(val);
	val = getenv("ROOT_CONSTR_MIN_UNSET");
	if (val)
		g_constr_min_unset = atof(val);
	val = getenv("ROOT_CONSTR_MAX_UNSET");
	if (val)
		g_constr_max_unset = atof(val);
	val = getenv("ROOT_PERIOD_BASE");
	if (val)
		g_period_base = atoi(val);
	val = getenv("ROOT_PERIOD_COEF1");
	if (val)
		g_period_coef1 = atoi(val);
	val = getenv("ROOT_PERIOD_COEF2");
	if (val)
		g_period_coef2 = atoi(val);
	initialized = 1;
}
#endif

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
	if (unset_ratio < 0.2)
		return (0);
	x = 1 - unset_ratio;
#if !defined(G_PRUNE_NO_ENV) || !G_PRUNE_NO_ENV
	init_env();
#endif
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
