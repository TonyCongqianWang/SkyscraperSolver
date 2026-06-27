# Agent Insights: Hyperparameter Optimization (HPO) for Skyscraper Solver

This document summarizes our core findings, architectural trade-offs, and critical insights discovered during hyperparameter optimization (HPO) of the Skyscraper Solver.

---

## 💡 1. The Crucial Role of Deep Subtree Pruning

The most important discovery during our HPO iterations is that **deep pruning (GAC and Check Constraints) is absolutely essential for solving hard instances**.

* **The Trap of Easy Puzzles**:
  Easy or medium-difficulty puzzles have short search trees. For these instances, lookahead and GAC checks introduce more CPU overhead than they save in node count. As a result, when optimizing globally across a mixture of easy/medium tasks, a standard HPO sweep will greedily drive the parameters to disable deep pruning (e.g., setting `DEEP_MIN_UNSET = 0.5` or `DEEP_GAC_UNSET_THRESHOLD = 0.8`), which speeds up easy cases.
* **The Hard Puzzle Explosion**:
  When deep pruning is disabled, the solver suffers from a **catastrophic search-space explosion on harder puzzles**. On our validation set of hard Size 9 puzzles:
  * With deep pruning disabled: solving took **47.27 seconds** (7.7 million nodes).
  * With deep pruning enabled (baseline): solving took only **7.53 seconds** (2.0 million nodes).
  
  **Insight**: A successful optimization must prioritize the exponential scaling of hard instances by maintaining strong, active pruning at deep search levels (using low `g_min_unset_threshold` values like `0.044`).

---

## 📈 2. Strategy Routing & Depth Dynamics

The solver segments its search-tree depth into three strategies: **Shallow**, **Medium**, and **Deep**. The transitions between these strategies are governed by:
* `ROUTING_SHALLOW_RATIO` (default `0.05` of $S^2$)
* `ROUTING_MEDIUM_RATIO` (default `0.27` of $S^2$)

### Trade-offs:
* **Shallow vs. Medium Routing**:
  Tuning indicates that keeping `ROUTING_SHALLOW_RATIO` small (e.g. `0.02` to `0.05`) is optimal. This ensures the solver quickly transitions into the medium strategy where constraint checking can prune values.
* **Medium vs. Deep Routing**:
  The transition to deep pruning should happen relatively early for hard puzzles. For Size 9 ($S^2 = 81$), setting `ROUTING_MEDIUM_RATIO = 0.27` routes search nodes to deep strategy starting at depth 23, ensuring that GAC checks and lookahead can restrict the search space before branches multiply exponentially.

---

## 🎯 3. Calibrated Datasets for Single-Solution Search

To prevent HPO from being biased by easy enumeration puzzles, we curated specific **calibrated single-solution benchmark sets** where all puzzles:
1. Are solvable in reasonable time (0.4s to 15.0s on baseline).
2. Are verified to be solvable across all 8 orientations (rotations and reflections) in under 30.0s (to ensure search-order robustness).

These datasets are located under `benchmark_sets/calibrated_single_solution/`:
* `benchmarkSet9_calibrated.txt`: Medium-difficulty baseline Size 9 puzzles.
* `benchmarkSet9_calibrated_harder_v2.txt`: Harder Size 9 puzzles serving as the ultimate test of the pruning routines' subtree-compression power.
