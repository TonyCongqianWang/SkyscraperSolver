#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"

python -u "$SCRIPT_DIR/solve_sky.py" "$@"
