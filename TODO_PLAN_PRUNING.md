# Pruning Strategy Pattern Plan

This document details the refactoring of the pruning engine to support a dynamic "Strategy Pattern". The goal is to separate the pruning logic from the search process, allowing different pruning algorithms and configurations to be chosen depending on the search node's state (depth, size, unset ratio, etc.).

---

## 1. Data Structures & Types

We define standard short typedefs in `src/puzzle_structs.h`:

```c
typedef unsigned short      t_u16;
typedef unsigned long long  t_u64;
```

We define the configuration structures in `src/strategy_config.h` using hardcoded constant configurations:

```c
#ifndef STRATEGY_CONFIG_H
# define STRATEGY_CONFIG_H

typedef enum e_prune_strategy
{
	PRUNE_LOOKAHEAD_DIVE,
	PRUNE_GAC,
	PRUNE_HYBRID,
	PRUNE_NONE
}	t_prune_strategy;

typedef struct s_lookahead_config
{
	int		is_selective;       /* 1 = only row/col of recent insertions, 0 = all empty cells */
	int		max_depth;          /* Depth limit (X) */
	int		branching_budget;   /* Max branches to explore (Y) */
	int		enable_node_select; /* Use smart node selection during dive */
	int		pruning_level;      /* 0 = simple, 1 = advanced */
}	t_lookahead_config;

typedef struct s_gac_config
{
	int		is_selective;       /* 1 = only row/col of recent insertions, 0 = all */
	int		max_k;              /* Max tuple size (default is 3, but algorithm generalizes) */
	int		analyse_naked;      /* Enable naked tuple analysis */
	int		analyse_hidden;     /* Enable hidden tuple analysis */
}	t_gac_config;

typedef struct s_prune_config
{
	t_prune_strategy	strategy;
	t_lookahead_config	lookahead;
	t_gac_config		gac;
}	t_prune_config;

#endif
```

---

## 2. Selective Tracking (Bitmask Mechanics)

To make selective pruning/GAC extremely fast without traversing lists or history arrays, we add two bitmasks of type `t_u16` to `t_node_state` in `src/puzzle_structs.h`:

```c
typedef struct s_node_state
{
	/* ... existing fields ... */
	t_u16					rows_changed_since_prune;
	t_u16					cols_changed_since_prune;
	/* ... existing fields ... */
}	t_node_state;
```

### Updates in `grid_manipulation.c`:
Whenever `set_grid_val` is called:
```c
state->rows_changed_since_prune |= (1 << (cell_idx / state->size));
state->cols_changed_since_prune |= (1 << (cell_idx % state->size));
```

### Reset in `prune_node`:
After pruning is performed:
```c
state->rows_changed_since_prune = 0;
state->cols_changed_since_prune = 0;
```

---

## 3. Strategies Implementation

We will split the implementation into dedicated files to ensure functions are $\le 25$ lines and conform to the 42 Norm.

### A. Lookahead Dive Strategy (`src/prune_lookahead.c`)

This strategy runs depth-bounded or budget-bounded searches to find and eliminate inconsistent cell-value choices.

1. **BFS vs. DFS Cache Routing**:
   - Before executing the complete shallow BFS lookahead pass (evaluating level-1 constraints for all cells), set the flag `puzzle->cur_node->is_in_bfs_dive = 1`.
   - This routes cache queries and rebuilds to `order_caches[2]`.
   - When descending into a deeper recursive search dive (DFS lookahead), reset `is_in_bfs_dive = 0` so it routes to `order_caches[1]`.
   - Restore the flag when backtracking.

2. **Selective Filter**:
   If `config.is_selective` is enabled, loop over cells and check:
   ```c
   int row = cell_idx / size;
   int col = cell_idx % size;
   if (!((state->rows_changed_since_prune & (1 << row)) ||
         (state->cols_changed_since_prune & (1 << col))))
       continue; /* Skip lookahead for this cell */
   ```

3. **Diving Algorithm**:
   - For candidates passing the filter, call `do_l_ahead_dive`.
   - If `enable_node_select` is active, dive uses the configured node selection. Otherwise, it uses sequential next transition.
   - If `branching_budget` is set, restrict the total visited node count during the lookahead dive.

---

### B. Generalized Arc Consistency (GAC) Strategy (`src/prune_gac.c`)

GAC enforces constraint consistency on rows and columns. We analyze rows and columns to find naked and hidden tuples of size $k$ ($1 \le k \le \text{max\_k}$). The algorithm is designed to generalize to any size $k$, using recursive or iterative combination generators.

#### 1. General Combination Generator
To support any $k$ dynamically:
- Define a function `generate_combinations(int *pool, int pool_size, int k, int start, int depth, int *current, void (*callback)(t_node_state *state, int *comb, int k, ...))`
- This generates all combinations of $k$ indices/values and passes them to the solver callbacks.

#### 2. Naked Tuple Analysis
For a given row/column:
1. Gather all empty cells (into a pool of size $M$).
2. For each $k \in [1, \text{max\_k}]$ (where $k \le M$):
   - Generate all combinations of $k$ cells.
   - For each combination, compute the union of their valid value bitmasks:
     $$\text{union\_bmp} = \bigvee_{i=1}^{k} \text{valid\_val\_bmps}[\text{cell}_i]$$
   - Count the number of set bits in `union_bmp`.
   - If the number of set bits is $\le k$:
     - These $k$ values are restricted to these $k$ cells.
     - Eliminate these $k$ values from all *other* empty cells in the same row/column:
       ```c
       for each other empty cell 'c' in row/col:
           for each value 'v' in union_bmp:
               set_value_invalid(state, c, v);
       ```

#### 3. Hidden Tuple Analysis
For a given row/column:
1. For each value $v \in [1, S]$, compute a cell bitmask representing the empty cells in this row/col that can contain $v$:
   `t_u16 value_cells[MAX_SIZE];`
2. For each $k \in [1, \text{max\_k}]$:
   - Generate all combinations of size $k$ of the values.
   - For each combination, compute the union of their cell bitmasks:
     $$\text{union\_cells} = \bigvee_{i=1}^{k} \text{value\_cells}[\text{val}_i]$$
   - Count the number of set bits in `union_cells`.
   - If the number of set bits is $\le k$:
     - These $k$ values can only go into these $\le k$ cells.
     - Eliminate all *other* values from these $\le k$ cells:
       ```c
       for each cell 'c' in union_cells:
           for each value 'v' not in the combination:
               set_value_invalid(state, c, v);
       ```

---

## 4. Routing & Situational Configs (`src/strategy_routing.c`)

We define situational routing rules to select the best configuration:

```c
void	select_prune_config(t_puzzle *puzzle, t_prune_config *config)
{
	double	unset_ratio;

	unset_ratio = (double)puzzle->cur_node->num_unset / puzzle->squared_size;
	if (unset_ratio < g_min_unset_r_prune)
	{
		config->strategy = PRUNE_NONE;
		return ;
	}
	/* Use GAC at shallow levels where tuples are highly constrained */
	if (puzzle->cur_node->cur_depth < 3)
	{
		config->strategy = PRUNE_GAC;
		config->gac.is_selective = 0;
		config->gac.max_k = 3; /* Default k = 3, generalizes to other values */
		config->gac.analyse_naked = 1;
		config->gac.analyse_hidden = 1;
	}
	/* Use Lookahead Dive at deeper levels with selective filtering */
	else
	{
		config->strategy = PRUNE_LOOKAHEAD_DIVE;
		config->lookahead.is_selective = 1;
		config->lookahead.max_depth = 1;
		config->lookahead.branching_budget = 0;
		config->lookahead.enable_node_select = 1;
		config->lookahead.pruning_level = 1;
	}
}
```
