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

typedef enum e_selectivity_level
{
	SELECTIVITY_NONE,
	SELECTIVITY_ANY_CHANGE,
	SELECTIVITY_VALUE_SET
}	t_selectivity_level;

typedef struct s_constr_limits
{
	double	min_entropy;
	double	max_entropy;
	int		global_min_entropy;
}				t_constr_limits;

typedef struct s_check_mode
{
	int				run_constr;
	int				run_prop;
	int				run_gac;
	int				lookahead_continue_min_entropy;
	double			lookahead_continue_slope;
	t_constr_limits	constr;
	t_constr_limits	gac;
}				t_check_mode;

extern const t_check_mode	g_check_none;
extern const t_check_mode	g_check_constr;

typedef enum e_lookahead_pass
{
	LOOKAHEAD_NONE = 0,
	LOOKAHEAD_POS = 1 << 0,
	LOOKAHEAD_NEG = 1 << 1,
	LOOKAHEAD_BOTH = LOOKAHEAD_POS | LOOKAHEAD_NEG
}	t_lookahead_pass;

typedef struct s_lookahead_config
{
	t_selectivity_level	selectivity;
	int					max_depth;
	t_lookahead_pass	passes;
	t_check_mode		check_mode;
}	t_lookahead_config;

typedef struct s_gac_config
{
	t_selectivity_level	selectivity;
	int					max_k;
	int					analyse_naked;
	int					analyse_hidden;
	double				min_entropy;
	double				max_entropy;
	int					global_min_entropy;
}	t_gac_config;

typedef enum e_selection_criterion
{
	SELECT_MAX,
	SELECT_MIN
}	t_selection_criterion;

typedef struct s_node_select_config
{
	t_selection_criterion	criterion;
	int						rebuild_period;
	t_selectivity_level		selectivity;
}	t_node_select_config;

#endif
