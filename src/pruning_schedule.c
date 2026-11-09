/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   pruning_schedule.c                                 :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/26 11:52:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/26 11:52:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "pruning_configs.h"

static double	get_period_multiplier(int tier, double medium, double heavy)
{
	if (tier == PRUNE_LIGHT)
		return (1.0);
	if (tier == PRUNE_MEDIUM)
		return (medium);
	if (tier == PRUNE_HEAVY)
		return (heavy);
	return (2.0 * heavy);
}

static int	is_extra_enabled(const t_node_state *node)
{
	t_probe_depth	depth;

	depth = get_probe_depth(PRUNE_EXTRA, node->tree.lookahead_depth);
	return (depth.positive > 0 || depth.negative > 0);
}

int	select_prune_tier(const t_node_state *node, double period,
			double medium, double heavy)
{
	int		tier;
	double	multiplier;

	tier = 0;
	while (tier < PRUNE_TIER_COUNT)
	{
		if (tier != PRUNE_EXTRA || is_extra_enabled(node))
		{
			multiplier = get_period_multiplier(tier, medium, heavy);
			if (node->last_entropy[tier] - node->domain.remaining_entropy
				> period * multiplier)
				return (tier);
		}
		tier++;
	}
	return (-1);
}
