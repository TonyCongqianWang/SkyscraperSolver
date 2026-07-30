/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   params_math.h                                      :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/07/29 02:00:00 by towang            #+#    #+#             */
/*   Updated: 2026/07/29 02:00:00 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef PARAMS_MATH_H
# define PARAMS_MATH_H

/* General Math Parameter Defaults */
extern int		g_weight_cell_constr_ratio_fp;
extern int		g_weight_total_scale_fp;
extern double	g_global_entropy_unset_bias;
extern int		g_sel_weight_cell_constr_ratio_fp;
extern double	g_sel_power;

/* Size 7 Math Parameters */
extern int		g_weight_cell_constr_ratio_fp_s7;
extern int		g_weight_total_scale_fp_s7;
extern double	g_global_entropy_unset_bias_s7;
extern int		g_sel_weight_cell_constr_ratio_fp_s7;
extern double	g_sel_power_s7;

/* Size 8 Math Parameters */
extern int		g_weight_cell_constr_ratio_fp_s8;
extern int		g_weight_total_scale_fp_s8;
extern double	g_global_entropy_unset_bias_s8;
extern int		g_sel_weight_cell_constr_ratio_fp_s8;
extern double	g_sel_power_s8;

/* Size 9 Math Parameters */
extern int		g_weight_cell_constr_ratio_fp_s9;
extern int		g_weight_total_scale_fp_s9;
extern double	g_global_entropy_unset_bias_s9;
extern int		g_sel_weight_cell_constr_ratio_fp_s9;
extern double	g_sel_power_s9;

/* Size-indexed Accessors */
int				get_weight_cell_constr_ratio_fp(int size);
int				get_weight_total_scale_fp(int size);
double			get_global_entropy_unset_bias(int size);
int				get_sel_weight_cell_constr_ratio_fp(int size);
double			get_sel_power(int size);

#endif
