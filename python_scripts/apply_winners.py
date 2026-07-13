#!/usr/bin/env python3
import os
import sys
import re
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from param_metadata import PARAMETER_MAPPING

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
    import argparse
    parser = argparse.ArgumentParser(description="Apply SPSA winners to C sources and tune script defaults.")
    parser.add_argument("winners_file", help="Path to the winners file (e.g. scratch/ref_s9_combined.txt)")
    parser.add_argument("--no-update-tune", action="store_true", help="Do not update the tune script defaults (param_metadata.py).")
    args = parser.parse_args()
    
    winners = parse_winners(args.winners_file)
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
        unapply_script = os.path.join(SCRIPT_DIR, "examples", "apply_env_overrides.py")
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
                formatted_val = str(int(float(raw_val)))
            else:
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

    # Update param_metadata.py defaults unless disabled
    if not args.no_update_tune:
        metadata_path = os.path.join(SCRIPT_DIR, "param_metadata.py")
        if os.path.exists(metadata_path):
            with open(metadata_path, "r") as f:
                meta_content = f.read()
                
            meta_original = meta_content
            for name, value in winners.items():
                if name not in PARAMETER_MAPPING:
                    continue
                _, _, var_type = PARAMETER_MAPPING[name]
                if var_type == "int":
                    formatted_val = str(int(float(value)))
                else:
                    formatted_val = f"{float(value):.15g}"
                    
                # Match: ("NAME", min, max, default, type, ...)
                pattern = re.compile(rf'(\(\s*"{name}"\s*,\s*[^,]+\s*,\s*[^,]+\s*,\s*)([^,]+)(\s*,\s*\w+.*?\))')
                if pattern.search(meta_content):
                    meta_content = pattern.sub(rf'\g<1>{formatted_val}\g<3>', meta_content)
                    print(f"[param_metadata.py] Updated {name} default -> {formatted_val}")
                    
            if meta_content != meta_original:
                with open(metadata_path, "w") as f:
                    f.write(meta_content)
                print(f"Saved changes to {metadata_path}")
        else:
            print(f"Warning: param_metadata.py not found at {metadata_path}")

if __name__ == "__main__":
    main()
