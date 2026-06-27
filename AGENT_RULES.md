# Agent Rules: Cooperative Guidelines & Constraints

This document defines the behavioral boundaries, design guidelines, and cooperative rules for AI agents working on the Skyscraper Solver repository.

---

## 🚫 1. Prevent Overeager Behavior (Report Back First)

AI coding agents are prohibited from chain-executing major optimization phases, compiling experimental setups, or launching benchmark runs automatically.

* **The Checkpoint Rule**:
  Whenever a major step is completed (e.g., an SPSA sweep, a validation run, or a dataset calibration), the agent **must immediately stop and report the results** to the user.
* **No Auto-Resume**:
  Agents must never automatically revert strategy files, clean-rebuild the codebase, or trigger a new sweep based on performance findings without first requesting and receiving **explicit user approval**.

---

## 🛑 2. Honor "STOP ASAP" Directives Immediately

When the user issues a `STOP` command or requests a quick check on tool availability/compilation setup:
* Halting all active executions, background sweeps, or pending terminal commands immediately is mandatory.
* Clean up any running background PIDs or orphan processes.
* **Preserve Work**: Do **NOT** revert, delete, or discard any code modifications, progress, or files generated during the session. Leave the workspace exactly in its current state so that prior compute and development resources are not wasted.
* Report the exact status and changes back to the user without attempting any recovery scripts or automated workarounds.

---

## 💻 3. Portability & Path Safety (No Machine Leakage)

To ensure that the repository remains fully portable across different machines, environments, and operating systems:
* **No Absolute Paths**: Agents must never hardcode machine-specific absolute file paths (such as `C:\Users\...\SkyscraperSolver`).
* **Relative Resolution**: Always resolve directory paths dynamically in scripts using relative paths calculated from the script file location itself:
  ```python
  import os
  SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
  ROOT_DIR = os.path.dirname(SCRIPT_DIR)
  ```
* **Build Configuration**: Keep the `Makefile` clean and pass customization parameters (like overrides) via standard environment variables or compiler flags.

---

## 📂 4. Temporary Files & Walkthrough Isolation (`scratch/`)

To prevent cluttering the repository and to avoid accidentally staging or committing transient developer files:
* **Strict Scratch Containment**: All temporary scripts, experimental analysis files, debug dumps, and test logs must be saved strictly within the `scratch/` directory.
* **Walkthroughs**: Walkthroughs documenting active refactoring steps or testing results (e.g., `walkthrough_refactor.md`) must be placed inside the `scratch/` directory (e.g., `scratch/walkthrough_refactor.md`) rather than in tracked root folders.
* **Git Excluded**: The `scratch/` directory is git-ignored, ensuring these files are never staged or committed.
