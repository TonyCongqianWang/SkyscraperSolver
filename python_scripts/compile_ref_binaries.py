#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse

def run_cmd(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    res = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"Error: {res.stderr.strip()}", file=sys.stderr)
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Compile specific git refs of skyscraper_solver.")
    parser.add_argument("refs", nargs="*", default=["v07", "v08", "main"], 
                        help="Git refs/tags/branches to compile (default: v07 v08 main)")
    args = parser.parse_args()

    # Keep track of original ref and branch name
    orig_ref = subprocess.run(
        ["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    
    branch_res = subprocess.run(
        ["git", "symbolic-ref", "--short", "-q", "HEAD"], capture_output=True, text=True
    )
    orig_branch = branch_res.stdout.strip() if branch_res.returncode == 0 else None
    
    # Check for uncommitted changes
    has_changes = subprocess.run(["git", "diff", "--quiet"], capture_output=True).returncode != 0
    if has_changes:
        print("Stashing local changes to prevent checkout conflicts...")
        run_cmd(["git", "stash"])
        
    try:
        for ref in args.refs:
            # Clean ref name for filename (replace slashes/special characters)
            clean_ref = ref.replace("/", "_").replace("\\", "_")
            bin_name = f"skyscraper_solver_{clean_ref}"
            
            print(f"\n=== Compiling git ref '{ref}' as '{bin_name}' ===")
            if not run_cmd(["git", "checkout", ref]):
                print(f"Error: Failed to checkout git ref '{ref}'")
                continue
                
            # Collect all C files in src/
            src_dir = "src"
            if not os.path.exists(src_dir):
                print(f"Error: src directory not found for ref '{ref}'")
                continue
                
            src_files = []
            for f in os.listdir(src_dir):
                if f.endswith(".c"):
                    src_files.append(os.path.join(src_dir, f))
                    
            if not src_files:
                print(f"Error: No C source files found in '{src_dir}' for ref '{ref}'")
                continue
                
            # Compile using gcc
            gcc_cmd = ["gcc", "-Wall", "-Wextra", "-O2"] + src_files + ["-o", bin_name]
            if not run_cmd(gcc_cmd):
                print(f"Error: Compilation failed for ref '{ref}'")
                continue
                
            print(f"Successfully compiled {bin_name}")
            
    finally:
        # Restore original state
        print("\nRestoring original branch/commit...")
        if orig_branch:
            subprocess.run(["git", "checkout", orig_branch], capture_output=True)
        else:
            subprocess.run(["git", "checkout", orig_ref], capture_output=True)
            
        if has_changes:
            print("Unstashing local changes...")
            subprocess.run(["git", "stash", "pop"], capture_output=True)

if __name__ == "__main__":
    main()
