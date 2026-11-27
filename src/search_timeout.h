#ifndef SEARCH_TIMEOUT_H
# define SEARCH_TIMEOUT_H
# include "types.h"

void search_timeout_init(void);
int search_timeout_check(t_node_count main_nodes);
void search_timeout_report(void);
double search_timeout_cpu_seconds(void);

#endif
