/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   node_selection_cache_copy.c                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/30 17:40:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/30 17:40:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "node_selection_cache.h"

void	copy_order_items(t_order_items *target, const t_order_items *source)
{
	int	i;

	target->count = source->count;
	i = -1;
	while (++i < source->count)
	{
		target->entries[i] = source->entries[i];
		target->meta[i] = source->meta[i];
	}
}

void	copy_node_order(t_node_order *target, const t_node_order *source)
{
	target->state = source->state;
	copy_order_items(&target->items, &source->items);
}
