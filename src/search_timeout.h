/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   search_timeout.h                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/11/27 18:21:38 by towang            #+#    #+#             */
/*   Updated: 2026/11/28 13:37:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef SEARCH_TIMEOUT_H
# define SEARCH_TIMEOUT_H
# include "types.h"

void	search_timeout_init(void);
int		search_timeout_check(t_node_count main_nodes);
void	search_timeout_report(void);
double	search_timeout_cpu_seconds(void);
int		search_timeout_cpu_nanoseconds(unsigned long long *ns);

#endif
