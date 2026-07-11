/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   strategy_config.h                                  :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/06/09 16:48:00 by towang            #+#    #+#             */
/*   Updated: 2026/06/09 16:48:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef STRATEGY_CONFIG_H
# define STRATEGY_CONFIG_H

typedef enum e_prune_strategy
{
	PRUNE_LOOKAHEAD_DIVE,
	PRUNE_GAC,
	PRUNE_HYBRID,
	PRUNE_NONE
}	t_prune_strategy;

typedef enum e_selectivity_level
{
	SELECTIVITY_NONE,
	SELECTIVITY_ANY_CHANGE,
	SELECTIVITY_VALUE_SET
}	t_selectivity_level;

typedef struct s_check_mode
{
	int		run_constr;
	int		run_prop;
	int		run_gac;
	double	downgrade_fraction;
	double	min_unset;
	double	max_unset;
	double	global_min_unset;
}				t_check_mode;

extern const t_check_mode	g_check_none;
extern const t_check_mode	g_check_constr;

typedef struct s_lookahead_config
{
	t_selectivity_level	selectivity;
	int					max_depth;
	int					branching_budget;
	int					enable_node_select;
	int					pruning_level;
	t_check_mode		check_mode;
}	t_lookahead_config;

typedef struct s_gac_config
{
	t_selectivity_level	selectivity;
	int					max_k;
	int					analyse_naked;
	int					analyse_hidden;
	double				min_unset;
	double				max_unset;
	double				global_min_unset;
}	t_gac_config;

typedef struct s_prune_config
{
	t_prune_strategy	strategy;
	t_lookahead_config	lookahead;
	t_gac_config		gac;
}	t_prune_config;

typedef enum e_score_family
{
	SCORE_BRANCHING,
	SCORE_MIN_CANDIDATES,
	SCORE_PROGRESS
}	t_score_family;

typedef enum e_selection_criterion
{
	SELECT_MAX,
	SELECT_MIN
}	t_selection_criterion;

typedef struct s_node_select_config
{
	t_score_family			score_family;
	t_selection_criterion	criterion;
	int						enable_cache;
	int						rebuild_period;
	int						start_cell_idx;
	char					start_cell_val;
	t_selectivity_level		selectivity;
}	t_node_select_config;

#endif
