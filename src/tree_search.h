/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   tree_search.h                                     :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/25 11:55:46 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:29:51 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef TREE_SEARCH_H
# define TREE_SEARCH_H
# include "puzzle_structs.h"

t_sol_info	tree_search(t_puzzle *puzzle);
t_sol_info	tree_recursion(t_puzzle *puzzle, t_node_transition next);

#endif
