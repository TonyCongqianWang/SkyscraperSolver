#!/bin/bash
# Exit on any error
set -e

tuner=python_scripts/spsa_tune.py
if [ "${1:-}" = "--sweep" ]; then
    tuner=python_scripts/sweep_tune.py
    shift
    if [ "$#" -eq 0 ]; then
        python3 "$tuner" --help
        exit 2
    fi
fi
# Show help and reject malformed options before doing any compilation.
if [ "$#" -gt 0 ]; then
    for argument in "$@"; do
        if [ "$argument" = "--help" ] || [ "$argument" = "-h" ]; then
            python3 "$tuner" "$@"
            exit 0
        fi
    done
    python3 - "$tuner" "$@" <<'PY'
import importlib.util
import sys

sys.argv[0] = sys.argv.pop(1)
spec = importlib.util.spec_from_file_location("tuner", sys.argv[0])
sys.path.insert(0, "python_scripts")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module.parse_args()
PY
fi

echo "=== Step 1: Compiling clean baseline solver ==="
make fclean
make

echo "=== Step 2: Saving baseline solver ==="
cp skyscraper_solver skyscraper_solver_main
echo "Saved baseline to: ./skyscraper_solver_main"

echo "=== Step 3: Injecting environment overrides ==="
python3 python_scripts/examples/apply_env_overrides.py

echo "=== Step 4: Rebuilding tunable solver ==="
make re
echo "Saved tunable solver to: ./skyscraper_solver"

# The work executable must see the same environment-overridable
# parameters as the native tunable solver. Build before unapplying patches.
objective=work
for argument in "$@"; do
    if [ "$argument" = "--nodes-time" ]; then
        objective=nodes-time
    fi
done
if [ "$objective" = "work" ]; then
    echo "=== Step 4b: Compiling instrumented tunable solver ==="
    make INSTRUMENT=1 clean
    make INSTRUMENT=1
fi

echo "=== Step 5: Unapplying environment overrides ==="
python3 python_scripts/examples/apply_env_overrides.py --unapply

echo "=========================================================="
echo "Setup Complete!"
echo "=========================================================="
echo "You can now run the SPSA tuning script, for example:"
echo "  python3 python_scripts/spsa_tune.py --size 7 --iterations 100 --log scratch/s7_tune.log"
echo "  python3 python_scripts/spsa_tune.py --size 8 --iterations 100 --log scratch/s8_tune.log"
echo "  python3 python_scripts/spsa_tune.py --size 9 --iterations 100 --log scratch/s9_tune.log"
echo "=========================================================="

# --sweep is recognized only in the first argument position.
if [ "$#" -gt 0 ]; then
    echo "Running $tuner with provided arguments..."
    python3 -u "$tuner" "$@"
fi
