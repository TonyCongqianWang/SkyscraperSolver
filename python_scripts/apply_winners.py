#!/usr/bin/env python3
import os
import sys
import re
import subprocess

# Map SPSA parameter names to C file, variable name, and type
PARAMETER_MAPPING = {
    # ROUTING
    "ROUTING_SHALLOW_RATIO": ("src/prune_strat_routing.c", "g_routing_shallow_ratio", "double"),
    "ROUTING_MEDIUM_RATIO": ("src/prune_strat_routing.c", "g_routing_medium_ratio", "double"),
    # ROOT
    "ROOT_GAC_UNSET_THRESHOLD": ("src/prune_strat_root.c", "g_gac_unset_threshold", "double"),
    "ROOT_CONSTR_MIN_UNSET": ("src/prune_strat_root.c", "g_constr_min_unset", "double"),
    "ROOT_CONSTR_MAX_UNSET": ("src/prune_strat_root.c", "g_constr_max_unset", "double"),
    "ROOT_PERIOD_BASE": ("src/prune_strat_root.c", "g_period_base", "int"),
    "ROOT_PERIOD_COEF1": ("src/prune_strat_root.c", "g_period_coef1", "int"),
    "ROOT_PERIOD_COEF2": ("src/prune_strat_root.c", "g_period_coef2", "int"),
    # SHALLOW
    "SHALLOW_MIN_UNSET": ("src/prune_strat_shallow.c", "g_min_unset_threshold", "double"),
    "SHALLOW_GAC_UNSET_THRESHOLD": ("src/prune_strat_shallow.c", "g_gac_unset_threshold", "double"),
    "SHALLOW_CONSTR_MIN_UNSET": ("src/prune_strat_shallow.c", "g_constr_min_unset", "double"),
    "SHALLOW_CONSTR_MAX_UNSET": ("src/prune_strat_shallow.c", "g_constr_max_unset", "double"),
    "SHALLOW_PERIOD_BASE": ("src/prune_strat_shallow.c", "g_period_base", "int"),
    "SHALLOW_PERIOD_COEF1": ("src/prune_strat_shallow.c", "g_period_coef1", "int"),
    "SHALLOW_PERIOD_COEF2": ("src/prune_strat_shallow.c", "g_period_coef2", "int"),
    # MEDIUM
    "MEDIUM_MIN_UNSET": ("src/prune_strat_medium.c", "g_min_unset_threshold", "double"),
    "MEDIUM_GAC_UNSET_THRESHOLD": ("src/prune_strat_medium.c", "g_gac_unset_threshold", "double"),
    "MEDIUM_CONSTR_MIN_UNSET": ("src/prune_strat_medium.c", "g_constr_min_unset", "double"),
    "MEDIUM_CONSTR_MAX_UNSET": ("src/prune_strat_medium.c", "g_constr_max_unset", "double"),
    "MEDIUM_PERIOD_BASE": ("src/prune_strat_medium.c", "g_period_base", "int"),
    "MEDIUM_PERIOD_COEF1": ("src/prune_strat_medium.c", "g_period_coef1", "int"),
    "MEDIUM_PERIOD_COEF2": ("src/prune_strat_medium.c", "g_period_coef2", "int"),
    # DEEP
    "DEEP_MIN_UNSET": ("src/prune_strat_deep.c", "g_min_unset_threshold", "double"),
    "DEEP_GAC_UNSET_THRESHOLD": ("src/prune_strat_deep.c", "g_gac_unset_threshold", "double"),
    "DEEP_CONSTR_MIN_UNSET": ("src/prune_strat_deep.c", "g_constr_min_unset", "double"),
    "DEEP_CONSTR_MAX_UNSET": ("src/prune_strat_deep.c", "g_constr_max_unset", "double"),
    "DEEP_PERIOD_BASE": ("src/prune_strat_deep.c", "g_period_base", "int"),
    "DEEP_PERIOD_COEF1": ("src/prune_strat_deep.c", "g_period_coef1", "int"),
    "DEEP_PERIOD_COEF2": ("src/prune_strat_deep.c", "g_period_coef2", "int"),
    # SELECTIVITY
    "SEL_REBUILD_PERIOD": ("src/sel_strat_routing.c", "g_sel_rebuild_period", "double"),
    "SEL_ORD2_COEFF": ("src/sel_strat_routing.c", "g_sel_ord2_coeff", "double"),
    "SEL_ORD4_COEFF": ("src/sel_strat_routing.c", "g_sel_ord4_coeff", "double"),
}

def parse_winners(winners_path):
    parsed = {}
    if not os.path.exists(winners_path):
        print(f"Error: Winners file '{winners_path}' not found.", file=sys.stderr)
        sys.exit(1)
        
    with open(winners_path, "r") as f:
        for line in f:
            line = line.strip()
            # Format A: Name = Val
            if "=" in line and not line.startswith("#"):
                parts = line.split("=")
                if len(parts) >= 2:
                    name = parts[0].strip()
                    val = parts[1].strip()
                    parsed[name] = val
            # Format B: #define Name Val
            elif line.startswith("#define"):
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[1].strip()
                    val = parts[2].strip()
                    parsed[name] = val
    return parsed

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 apply_winners.py <winners_file_path>")
        sys.exit(1)
        
    winners_path = sys.argv[1]
    winners = parse_winners(winners_path)
    if not winners:
        print("No valid parameters found in the winners file.")
        sys.exit(1)
        
    # Check if overrides are currently applied
    needs_unapply = False
    for name in PARAMETER_MAPPING:
        filepath, _, _ = PARAMETER_MAPPING[name]
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                content = f.read()
            if "getenv" in content:
                needs_unapply = True
                break
                
    if needs_unapply:
        print("Detected active env overrides in C source files. Unapplying first...")
        script_dir = os.path.dirname(os.path.abspath(__file__))
        unapply_script = os.path.join(script_dir, "examples", "apply_env_overrides.py")
        if os.path.exists(unapply_script):
            subprocess.run([sys.executable, unapply_script, "--unapply"], check=True)
        else:
            print("Warning: unapply script not found. Proceeding with direct replacement.")

    # Group updates by file to minimize open/close operations
    by_file = {}
    for name, value in winners.items():
        if name not in PARAMETER_MAPPING:
            continue
        filepath, var_name, var_type = PARAMETER_MAPPING[name]
        by_file.setdefault(filepath, []).append((var_name, var_type, value))

    for filepath, updates in by_file.items():
        if not os.path.exists(filepath):
            print(f"Warning: File '{filepath}' not found. Skipping updates.")
            continue
            
        with open(filepath, "r") as f:
            content = f.read()
            
        original_content = content
        for var_name, var_type, raw_val in updates:
            # Format value based on variable type
            if var_type == "int":
                # Convert to integer
                formatted_val = str(int(float(raw_val)))
            else:
                # Retain float representation
                formatted_val = f"{float(raw_val):.15g}"
                
            # Regex pattern to match: static [const] type name = value;
            pattern = re.compile(rf'(static\s+(?:const\s+)?{var_type}\s+{var_name}\s*=\s*)([^;]+)(;)')
            match = pattern.search(content)
            if match:
                old_val = match.group(2).strip()
                content = pattern.sub(rf'\g<1>{formatted_val}\g<3>', content)
                print(f"[{filepath}] Updated {var_name}: {old_val} -> {formatted_val}")
            else:
                print(f"Warning: Could not find declaration for '{var_name}' of type '{var_type}' in '{filepath}'")
                
        if content != original_content:
            with open(filepath, "w") as f:
                f.write(content)
            print(f"Saved changes to {filepath}")

if __name__ == "__main__":
    main()
