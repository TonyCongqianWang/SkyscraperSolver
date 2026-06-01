# Plan: Cache and Reuse Node Orderings

> This plan covers the item described in **TODOS.md §"Cache and Reuse Node Orderings #2"** (see there for the brief description and motivation). This document details the full technical design and implementation strategy.

---

## 1. Problem Analysis

### Current Flow (every call to `tree_search`)

1. `try_get_best_transition` (`node_selection.c`) loops over **all** `S²` cells.
2. For each empty cell, `set_best_val` scores each valid value via `score_transition_constrs` → reading `num_val_positions` from `t_constrs_state` and `valid_val_bmps` from `t_grid_state`.
3. The best-scoring candidate then gets a full score via `score_transition_full`, which reads `get_col_num_valids`, `get_row_num_valids`, `get_cell_num_valids`.
4. The full scan repeats at every node — even when little has changed.

For an 8×8 grid: each call scans 64 cells × 8 values = ~512 scoring operations just to pick the next move.

### What actually changes between calls?

This is the critical insight that must be modelled correctly.

**`set_value_invalid(cell_idx, val)`** (`grid_manipulation.c`) is the primitive that changes scores. It:
- Clears the bit `val` from `valid_val_bmps[cell_idx]`
- Calls `decrement_cell_num_valids(cell_idx)` → changes `num_cell_vals[cell_idx]`, and may trigger `set_grid_val` via `set_valid_val_cell` (forced assignment) if only one value remains
- Calls `decrement_constr_num_valids(cell_idx, val)` → decrements `num_val_positions[col_constr][val-1]` AND `num_val_positions[row_constr][val-1]`, and may trigger forced `set_grid_val` calls via `set_val_in_col` / `set_val_in_row`

**Score-affecting consequences per `set_value_invalid(cell_idx, val)` call:**
- `cell_idx`'s own score changes (`num_valids_cell` drops).
- Every other empty cell sharing the **same column constraint** whose score depends on `num_valids_col` for `val` now has a stale score.
- Every other empty cell sharing the **same row constraint** whose score depends on `num_valids_row` for `val` now has a stale score.

**`set_value_invalid` is called in many contexts:**
1. Inside `update_availability` (called by `set_grid_val`) — every time a value is placed, this eliminates `val` from the entire row and column.
2. Inside `prune_node` — after a lookahead dive fails, arbitrary `(cell_idx, val)` pairs are invalidated across the entire grid.
3. Indirectly via `decrement_constr_num_valids` → `set_val_in_col` / `set_val_in_row` → `set_grid_val` → `update_availability` → more `set_value_invalid` calls (a cascade).
4. Directly in `search_step` as the backtrack invalidation: `set_value_invalid(next.cell_idx, next.cell_val)`.

**Conclusion:** A single `set_value_invalid` can make the scores of cells in the same row OR column stale. Since cascades can propagate this to arbitrary rows and columns, a fully correct incremental update must either track every affected cell precisely or accept that stale data is possible and control how often a full rebuild is done.

---

## 2. Proposed Design: Frequency-Controlled Full Rebuild

Rather than attempting a fine-grained incremental update (complex, fragile), the key insight is that we already have a good proxy for "how much has changed": **`progress_counter`**, the same counter used by `skip_pruning` (see AGENT_NOTES.md §2A).

Each `set_value_invalid` call increments `progress_counter` by 1. Each `set_grid_val` increments it by 10. So `progress_counter` already tracks the total amount of grid state change since the last prune.

We use `progress_counter` in the same way to decide when the cached order is too stale to use without rebuilding.

### Data Structure: `t_node_order`

```c
// In puzzle_structs.h
# define MAX_ORDER_COUNT MAX_CELL_COUNT

typedef struct s_node_order
{
    t_node_transition   entries[MAX_ORDER_COUNT];
    int                 count;
    t_prune_prog        last_build_prog;  // value of progress_counter when cache was built
}   t_node_order;
```

Add to `t_node_state`:
```c
t_node_order    order_cache;
```

> **Norminette note (see AGENT_NOTES.md §3):** Tab-align member names at column 25. `t_node_order` follows the established naming pattern.

### When to rebuild vs. reuse

Define a global tunable threshold `g_order_rebuild_period` (analogous to `g_prune_period_shallow`):

```c
const t_prune_prog  g_order_rebuild_period = 8; // tunable
```

Before calling `get_best_from_cache`, check:

```c
int order_is_stale(t_node_state *node)
{
    return (node->progress_counter >=
            node->order_cache.last_build_prog + g_order_rebuild_period);
}
```

If stale → full rebuild + update `last_build_prog`.  
If fresh → return `entries[0]` (the best pre-sorted entry) directly in O(1).

### Handling removed entries (set cells)

When a cell gets set via `set_grid_val`, it is no longer a candidate. Rather than rebuilding just for that:
- On cache reuse, skip entries whose `cell_idx` is no longer empty (check `is_cell_empty`).
- This keeps the reuse path trivial without requiring an explicit remove step.

---

## 3. Algorithm

### `build_node_order(puzzle)` — full rebuild

- Iterate all `S²` cells.
- For each empty cell, call `set_best_val` and `score_transition_full` (same as current logic).
- Store all scored candidates in `entries[]`.
- Sort descending by score (insertion sort, O(N), N ≤ 81).
- Set `last_build_prog = progress_counter`.

### `get_best_from_cache(puzzle, *next)` — main entry point

```
if order_is_stale(node):
    build_node_order(puzzle)
scan entries[] from front:
    skip set cells (is_cell_empty check)
    return first valid entry
if none found (all set or invalid):
    return 0
```

### Backtracking

Because `old_state = *(puzzle->cur_node)` saves the entire node including `order_cache` (and its `last_build_prog`), restoring `*(puzzle->cur_node) = old_state` fully restores the cache state for free. No extra handling needed.

---

## 4. Choosing `g_order_rebuild_period`

This is the key tunable. The tradeoff:
- **Too high**: cache goes stale → poor move ordering → more nodes explored.
- **Too low**: rebuilds too often → the benefit over the current approach shrinks.

A good starting heuristic: rebuild roughly every `~S` invalidations, i.e. `g_order_rebuild_period ≈ S` (around 7–8 for the primary benchmark sizes). This should be validated with the same grid search approach used for the pruning parameters (see AGENT_NOTES.md §4 for the tuning script template).

Two additional ideas for the future:
- **Scale the period with `unset_ratio`** (same as `skip_pruning`): rebuild less often deep in the tree where few cells remain and scoring changes matter less.
- **Hard-rebuild after pruning** (always): since pruning causes many invalidations across arbitrary rows/columns, always rebuild after a full `prune_node` call rather than waiting for the period. This avoids the worst-case stale ordering after a major pruning pass.

---

## 5. Integration Points

| Call site | File | Action |
|---|---|---|
| `try_get_best_transition` in `tree_search` loop | `tree_search.c` | Replace with `get_best_from_cache(puzzle, &next)` |
| After `prune_node` returns | `tree_search.c` | Force-rebuild: set `last_build_prog = progress_counter - g_order_rebuild_period` to mark stale |
| Inside lookahead dive | `node_pruning.c` | `try_get_next_transition` is used there (sequential, not best-first), unaffected |

---

## 6. New Files

| File | Purpose |
|---|---|
| `src/node_order.c` | `build_node_order`, `get_best_from_cache`, `order_is_stale` |
| `src/node_order.h` | Header; `t_node_order` struct goes in `puzzle_structs.h` instead |

---

## 7. Norminette & Function Size

Functions must stay ≤ 25 lines. Split responsibilities:
- `build_node_order`: loop + delegate to `fill_order_entries` + `sort_node_order`
- `fill_order_entries`: score all empty cells into `entries[]`
- `sort_node_order`: insertion sort on `entries[]`
- `get_best_from_cache`: stale check → rebuild → scan for first valid entry

Variable alignment at column 25 for `t_node_order` members (see AGENT_NOTES.md §3).

---

## 8. Correctness Risks & Mitigations

| Risk | Mitigation |
|---|---|
| Cache used when stale (invalidations happened) | `progress_counter` delta check → triggers rebuild within bounded staleness |
| Major staleness after large pruning pass | Force stale-mark after `prune_node` so next call always rebuilds |
| Set cells lingering in cache entries | Check `is_cell_empty` on reuse path; stale set-cell entries are skipped cheaply |
| Backtrack restores old `last_build_prog` pointing into past progress | Fine — the restored counter values are self-consistent; stale check still works |

---

## 9. Verification Plan

1. **Correctness**: Run the full Size 7 benchmark (`-s 0`, 200 cases) — all solution counts must match.
2. **Performance**: Compare the 10-case Size 8 benchmark against v08. Key expected gain: significant reduction in `score_transition_full` calls per node.
3. **Tuning**: Sweep `g_order_rebuild_period` values (e.g. 4, 8, 16, 32) using the existing tuning script template (see AGENT_NOTES.md §4) to find the optimal rebuild frequency.
4. **Norminette**: `norminette src/node_order.c src/node_selection.c src/puzzle_structs.h`
5. **Compilation**: `gcc -Wall -Wextra -Werror -O2 -o skyscraper_solver src/*.c`
