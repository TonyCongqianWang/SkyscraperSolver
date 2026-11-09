/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   search_verification.c                              :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:42 by towang            #+#    #+#             */
/*   Updated: 2026/06/18 16:17:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "check_node_validity.h"
#include "tree_search.h"

/* Strong verification belongs only to bounded, first-order probe leaves. */
t_check_mode	select_search_check_mode(const t_node_state *node,
				t_check_mode mode)
{
	t_leaf_state	leaf;

	if (node->tree.lookahead_depth == 0)
		return (mode);
	if (node->tree.lookahead_depth != 1)
		return (g_check_constr);
	leaf = classify_search_leaf(node);
	if (leaf != LEAF_DEPTH_LIMIT && leaf != LEAF_PROGRESS_LIMIT)
		return (g_check_constr);
	return (node->search_policy.leaf_check_mode);
}
