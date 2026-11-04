# Version History

### v09
Large-scale refactoring and tuning across the codebase, with agent-assisted development.
Expanded the benchmarking tools and added automated parameter tuning using SPSA.
Added CI checks to help verify correctness throughout development.

Completes the size 9 benchmark set in roughly 20 minutes on a 2.20 GHz Intel Xeon. This result is workload- and version-dependent; see earlier entries for historical comparisons.

Some regression in size 8 enumeration performance.

### v08
Added Python Z3 Cross-Checking Solver.
Added more auxiliary python scripts to measure and improve performance.
Refactored lookahead node pruning logic and integrated domain-specific type definitions and tuned parameters.

Solves the size 9 benchmark set in roughly 7:48 on a 2.20GHz Intel Xeon.

### v07
Added flag to allow searching for multiple solutions. Special case is 0, where solutions are not stored and output, instead only the number of solutions will be displayed at the end.

First version being able to solve the size 9 benchmarkset in roughly 7:59 on a 2.20GHz Intel Xeon.

### v06 / v06a / v06b
Added support for inputing grid values (v06) and empty constraint values (v06a). Changed program name in readme and benchmark scripts. Refactored and improved node pruning: Sacrificing a bit of speed for easier instances but being faster on harder ones.
Added bugfix in v06b and improved benchmarking. Bugfix has a very significant performance impact.

### v05
Solving process now sets cells as soon as only one value remains.

### v04
Added scripts to generate instances and for benchmarking. Refactored and improved constraint bound calculation slightly. Improved update of bounds / availability when marking values invalid. Added consideration of availability of values across columns / rows to the node selection heuristic.

### v03
Added arrays to keep track of cell bounds to allow more efficient calculations. Refactored node selection procedure to be more readable and maintainable. Constraint tightening now has the possibility to be iterated during early nodes to make use of cell bounds. Node selection now allows cell and value to be selected independently. Version v03 is somewhat work in progress, it regressed a lot in speed due to unecessary recalculations of constraints after trying every value instead of just once per node.

### v02 / v02a / v02b
Constraint calculation was changed to be more efficient and now takes lower and upper bounds of unset cells into consideration. Different print utilities were added to allow for easier understanding and debugging. In v02b debug prints are removed from main to reduce noisy outputs. Compared to v01 v02 is a lot faster on random 7x7 instances, but was slower on the few 9x9 example instances.

### v01
No algorithmic changes but lots of refactoring was done to clean up a few files and functions that got messy due to the projects time rectrictions as well as norminette.

### v00 / v00-fix
Submitted version for the piscine. Unfortunatly there was still a typo inside which caused invalid grids to be generated. In v00-fix this is fixed. This version also has no additional utilities and outputs the format exactly as specified in the projects subject.
