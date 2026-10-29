#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"
PYTHON="${PYTHON:-python3}"
BUILD_JOBS="${BUILD_JOBS:-4}"

# Help must work without building a solver or importing generation dependencies.
if [[ " ${*} " == *" --help "* || " ${*} " == *" -h "* ]]; then
    exec "$PYTHON" -m python_scripts.dataset_generation run --help
fi
"$PYTHON" -c 'import sys; assert sys.version_info >= (3, 11), "Python 3.11+ required"; import numpy, numba' || {
    echo "Install dependencies with your selected Python:" >&2
    echo "$PYTHON -m pip install -r python_scripts/dataset_generation/requirements.txt" >&2
    exit 1
}
make -j "$BUILD_JOBS"
exec "$PYTHON" -u -m python_scripts.dataset_generation run \
    --sizes 8 9 \
    --train-count 10000 --validation-count 1000 \
    --difficulty-mix 0.2 0.5 0.3 \
    --seed 20261029 --max-workers 4 \
    --timeout 8 --recheck-threshold 6.4 \
    --reference-count 500 --candidate-batch-size 2000 \
    --burn-in 100000 --gap 100 \
    "$@"
