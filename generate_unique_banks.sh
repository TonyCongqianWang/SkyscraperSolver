#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
make

# Stage 1: generate and uniqueness-check only minimal puzzles.
for size in 4 5 6 7 8 9; do
  count=1000
  if [[ "$size" -eq 4 ]]; then
    count=74
  fi
  echo "Generating size ${size}: ${count} canonical solutions (100000 attempts)" >&2
  "$PYTHON" python_scripts/puzzle_bank/generate_unique.py \
    --size "$size" --count "$count" --attempts 100000 \
    --minimal-only --output "$ROOT/puzzle_bank/unique/v1" "$@"
done

# Stage 2: draw mixed clue/given candidates from the generated minimal banks,
# verifying uniqueness with -s 2 and filling all minimum quotas.
"$PYTHON" python_scripts/puzzle_bank/fill_curated.py \
  --config "$ROOT/puzzle_bank/curated/v1/quotas.json" \
  --source "$ROOT/puzzle_bank/unique/v1/minimal" \
  --output "$ROOT/puzzle_bank/curated/v1" \
  --sizes 4 5 6 7 8 9
