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

/* Size <= 7 Math Parameters */
extern int		g_weight_cell_constr_ratio_fp_le7;
extern int		g_weight_total_scale_fp_le7;
extern double	g_global_entropy_unset_bias_le7;
extern int		g_sel_weight_cell_constr_ratio_fp_le7;
extern double	g_sel_power_le7;

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
