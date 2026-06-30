/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   stdin_tokenize.h                                   :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: towang <towang@student.42.fr>              +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2025/01/31 00:38:53 by towang            #+#    #+#             */
/*   Updated: 2025/01/31 00:38:53 by towang           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#ifndef STDIN_TOKENIZE_H
# define STDIN_TOKENIZE_H

int		tokenize_line(char *line, char **argv, int max_args);
int		has_stdin_flag(int argc, char **argv);
char	*find_max_solutions_arg(int argc, char **argv);

#endif
