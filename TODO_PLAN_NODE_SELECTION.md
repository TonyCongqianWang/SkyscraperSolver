# Node Selection Strategy Pattern Plan

This document details the refactoring of the node selection engine to support a dynamic "Strategy Pattern" combined with caching.

---

## 1. Data Structures & Types

To avoid long type names and improve code readability, we define standard short typedefs in `src/puzzle_structs.h`:

```c
typedef unsigned short      t_u16;
typedef unsigned long long  t_u64;

typedef t_u64               t_prune_prog;
typedef t_u64               t_sol_count;
typedef t_u64               t_node_count;
```

We define the configuration structures in `src/strategy_config.h`:

```c
#ifndef STRATEGY_CONFIG_H
# define STRATEGY_CONFIG_H

typedef enum e_score_family
{
	SCORE_BRANCHING,            /* Current constraint-checking & distance scoring */
	SCORE_MRV,                  /* Minimum Remaining Values (MRV) */
	SCORE_PROGRESS              /* Pruning feedback (lookahead progress-based) */
}	t_score_family;

typedef enum e_selection_criterion
{
	SELECT_MAX,                 /* Select transition with highest score */
	SELECT_MIN                  /* Select transition with lowest score */
}	t_selection_criterion;

typedef struct s_node_select_config
{
	t_score_family			score_family;
	t_selection_criterion	criterion;
	int						enable_cache;
	int						rebuild_period;
}	t_node_select_config;

#endif
```

We define the cached order structure in `src/puzzle_structs.h`:

```c
# define MAX_ORDER_COUNT MAX_CELL_COUNT
# define CACHE_COUNT 3

typedef struct s_node_order
{
	t_node_transition	entries[MAX_ORDER_COUNT];
	int					count;
	t_prune_prog		last_build_prog;  /* progress_counter value at cache build time */
}	t_node_order;
```

### The Three Order Caches
To prevent searches at different sub-levels from overwriting each other's cached orderings, we maintain **three** distinct caches in `t_node_state` (indexed dynamically based on the current context):

```c
t_node_order	order_caches[CACHE_COUNT];
```

The caches correspond to:
- `order_caches[0]`: Normal search (`sub_node_depth == 0`)
- `order_caches[1]`: Lookahead dives (`sub_node_depth > 0` and standard DFS search active)
- `order_caches[2]`: BFS lookahead dives (the complete shallow BFS pass of lookahead)

We add a flag to `t_node_state` to track when the BFS pass is active:
```c
int				is_in_bfs_dive;
```

A helper function retrieves the correct cache index:
```c
int	get_cache_index(t_node_state *node)
{
	if (node->sub_node_depth == 0)
		return (0);
	if (node->is_in_bfs_dive)
		return (2);
	return (1);
}
```

---

## 2. Default Initialization of Caches

Before any scoring or search steps run, all three order caches must be initialized to a valid, reasonable default ordering (e.g., ordering cell indices sequentially, and value options from 1 to $S$).

### Initialization Algorithm (`init_order_caches`):
- Loop over `order_caches[0...2]`.
- For each cache:
  - Set `count = puzzle->squared_size`.
  - Set `last_build_prog = 0`.
  - Populate `entries[i]` for $i \in [0, S^2-1]$:
    - `entries[i].cell_idx = i`
    - `entries[i].cell_val = 1`
    - `entries[i].score = 0.0`
    - `entries[i].num_valids_col = 0`
    - `entries[i].num_valids_row = 0`
    - `entries[i].num_valids_cell = 0`

This ensures that even if a cache is read before its first rebuild, it contains valid default moves.

---

## 3. Scoring Families Implementation

We will implement scoring in `src/node_selection_score.c`:

### A. SCORE_BRANCHING (Constraint & Distance Scoring)
This is the default heuristic currently in `transition_scoring.c`. It computes scores by:
- Querying constraints (`num_val_positions` in rows/columns).
- Factoring in cell distance to the edges of the grid.
- We select the maximum score (`SELECT_MAX`).

### B. SCORE_MRV (Minimum Remaining Values)
MRV selects the cell with the fewest valid options remaining in its domain:
- Score for cell `c` is simply `num_cell_vals[c]`.
- We select the minimum score (`SELECT_MIN`).

### C. SCORE_PROGRESS (Pruning-Feedback)
This heuristic runs a fast lookahead test on empty cells and tracks how many other cell domains were constrained as a result.
- Score is the delta of `progress_counter` during lookahead.
- Cells with higher progress values are selected (`SELECT_MAX`) since they propagate constraints the most.

---

## 4. Caching & Reuse Implementation (`src/node_selection_cache.c`)

When `enable_cache` is active, we store and reuse the sorted candidate list rather than rescanning and rebuilding it from scratch at every single search node.

### A. Stale Check
```c
int order_is_stale(t_node_state *node, t_node_select_config *config)
{
	int idx = get_cache_index(node);
	return (node->progress_counter >=
			node->order_caches[idx].last_build_prog + config->rebuild_period);
}
```

### B. Full Rebuild
- Determine the correct cache index `idx`.
- Iterate all empty cells in the grid.
- For each empty cell, evaluate candidates under the chosen `SCORE` family.
- Sort them in `order_caches[idx].entries[]` using insertion sort based on the `criterion` (ascending or descending).
- Save `order_caches[idx].last_build_prog = progress_counter`.

### C. Retrieval
- If the cache is stale, trigger a Full Rebuild.
- Scan the appropriate `order_caches[idx].entries[]` from the beginning.
- Skip cells that are no longer empty (checked using `is_cell_empty`).
- Return the first valid entry found.

---

## 5. Routing & Situational Configs (`src/strategy_routing.c`)

We define situational routing rules to select the best configuration:

```c
void	select_node_select_config(t_puzzle *puzzle, t_node_select_config *config)
{
	/* For highly determined nodes near the leaves, bypass cache and use MRV directly */
	if (puzzle->cur_node->num_unset < 12)
	{
		config->score_family = SCORE_MRV;
		config->criterion = SELECT_MIN;
		config->enable_cache = 0;
	}
	/* Otherwise, use cached BRANCHING scores to guide search efficiently */
	else
	{
		config->score_family = SCORE_BRANCHING;
		config->criterion = SELECT_MAX;
		config->enable_cache = 1;
		config->rebuild_period = 4; /* Default to 4 progress steps */
	}
}
```
