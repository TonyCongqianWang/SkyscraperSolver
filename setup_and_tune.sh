#!/bin/bash
# Exit on any error
set -e

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

# If arguments were passed to this script, execute spsa_tune.py with them
if [ "$#" -gt 0 ]; then
    echo "Running SPSA tune with provided arguments..."
    python3 -u python_scripts/spsa_tune.py "$@"
fi
