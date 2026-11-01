#!/usr/bin/env python3
"""Generate versioned minimal and augmented unique puzzle banks with the native solver."""
import argparse
import json
import random
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
def visibility(line):
    highest = count = 0
    for v in line:
        if v > highest:
            highest = v
            count += 1
    return count

def make_solution(n, rng):
    rows, cols, values = [list(range(n)) for _ in range(3)]
    for x in (rows, cols, values):
        rng.shuffle(x)
    return [[values[(r + c) % n] + 1 for c in cols] for r in rows]

def clues_for(g):
    n = len(g)
    return ([visibility([g[r][c] for r in range(n)]) for c in range(n)]
       + [visibility([g[r][c] for r in range(n-1, -1, -1)]) for c in range(n)]
       + [visibility(g[r]) for r in range(n)]
       + [visibility(g[r][::-1]) for r in range(n)])

def verify(binary, clues, cells, timeout, *, diagnose=False):
    try:
        p = subprocess.run([str(binary), "-s", "2", " ".join(map(str, clues)),
                            " ".join(map(str, cells))], text=True, capture_output=True,
                           timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        if diagnose:
            raise RuntimeError(f"Solver timed out after {timeout}s for clues={clues}, cells={cells}") from exc
        return None
    if p.returncode:
        if diagnose:
            raise RuntimeError(f"Solver exited {p.returncode} for clues={clues}, cells={cells}\\nstdout={p.stdout}\\nstderr={p.stderr}")
        return None
    m = re.search(r"^Solutions found:\s*(\d+)\s*$", p.stdout, re.M)
    nodes = re.search(r"^Nodes visited:\s*(\d+)\s*$", p.stdout, re.M)
    if not m or not nodes:
        if diagnose:
            raise RuntimeError(f"Solver output could not be parsed for clues={clues}, cells={cells}\\nstdout={p.stdout}\\nstderr={p.stderr}")
        return None
    return (int(m[1]), int(nodes[1]))

def minimize(binary, full, solved, rng, timeout, weight):
    n = len(solved)
    clues, cells = full[:], [0] * (n*n)
    if verify(binary, clues, cells, timeout) is None:
        return None
    if verify(binary, clues, cells, timeout)[0] != 1:
        positions = list(range(n*n))
        rng.shuffle(positions)
        for i in positions:
            cells[i] = solved[i//n][i%n]
            check = verify(binary, clues, cells, timeout)
            if check and check[0] == 1:
                break
        else:
            return None
    candidates = [(weight, 1, i) for i,v in enumerate(cells) if v]
    candidates += [(1, 0, i) for i,v in enumerate(clues) if v]
    rng.shuffle(candidates)
    candidates.sort(key=lambda x:-x[0])
    for _, is_cell, i in candidates:
        target = cells if is_cell else clues
        old = target[i]
        target[i] = 0
        test = verify(binary, clues, cells, timeout)
        if not test or test[0] != 1:
            target[i] = old
    test = verify(binary, clues, cells, timeout)
    return (clues, cells, test[1]) if test and test[0] == 1 else None

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--size",type=int,required=True,choices=range(4,10))
    ap.add_argument("--count",type=int,default=5)
    ap.add_argument("--attempts",type=int,default=100)
    ap.add_argument("--seed",type=int,default=12345)
    ap.add_argument("--weight",type=int,default=5)
    ap.add_argument("--timeout",type=float,default=10)
    ap.add_argument("--solver",type=Path,default=ROOT/"skyscraper_solver")
    ap.add_argument("--output",type=Path,default=ROOT/"puzzle_bank"/"unique"/"v1")
    args=ap.parse_args()
    if min(args.count,args.attempts,args.weight,args.timeout)<=0: ap.error("positive parameters required")
    binary=args.solver.resolve()
    if not binary.is_file(): ap.error("Build the native solver using make first")
    rng=random.Random(args.seed)
    minimal_bank=[]; graded_bank=[]; seen=set()
    for attempt in range(args.attempts):
        if len(minimal_bank)>=args.count: break
        solution=make_solution(args.size,rng)
        full=clues_for(solution)
        item=minimize(binary,full,solution,rng,args.timeout,args.weight)
        if item is None: continue
        clues,cells,nodes=item
        key=(tuple(clues),tuple(cells))
        if key in seen: continue
        seen.add(key)
        ident=f"s{args.size}-{len(minimal_bank)+1:05d}"
        base={"id":ident,"size":args.size,"clues":clues,"givens":cells,
              "solution":[v for row in solution for v in row],
              "clue_count":sum(bool(v) for v in clues),"given_count":sum(bool(v) for v in cells),
              "cost":sum(bool(v) for v in clues)+args.weight*sum(bool(v) for v in cells),
              "nodes_visited":nodes}
        minimal_bank.append(base)
        # Density variants are deliberately NOT presented as calibrated difficulty.
        missing=[i for i,v in enumerate(clues) if not v]
        rng.shuffle(missing)
        variants=[]
        for label,additional in [("minimal",0),("plus_2",2),("plus_4",4),("full",len(missing))]:
            variant=clues[:]
            for i in missing[:additional]: variant[i]=full[i]
            verified=verify(binary,variant,cells,args.timeout,diagnose=True)
            if verified[0]!=1:
                raise RuntimeError(f"Variant {label} for {ident} returned {verified[0]} solutions, expected 1. "
                                   f"Clues={variant}, givens={cells}, known solution={solution}")
            variants.append({"label":label,"clues":variant,"givens":cells,
                 "clue_count":sum(bool(v) for v in variant),"nodes_visited":verified[1]})
        graded_bank.append({"id":ident,"size":args.size,"variants":variants,
                            "difficulty_matched":False})
        print(f"Accepted {len(minimal_bank)}/{args.count} after {attempt+1} attempts",flush=True)
    if len(minimal_bank)!=args.count: raise SystemExit("Insufficient unique bases; no output written")
    out=args.output
    (out/"minimal").mkdir(parents=True,exist_ok=True)
    (out/"candidates").mkdir(parents=True,exist_ok=True)
    metadata={"schema_version":1,"size":args.size,"count":args.count,"seed":args.seed,
              "uniqueness":"verified by native solver -s 2","cell_weight":args.weight}
    (out/"minimal"/f"size_{args.size}.json").write_text(json.dumps({**metadata,"puzzles":minimal_bank},indent=2)+"\n")
    (out/"candidates"/f"size_{args.size}.json").write_text(json.dumps({**metadata,"status":"uncalibrated","puzzles":graded_bank},indent=2)+"\n")
    print(f"Wrote minimal and candidate banks to {out}")
if __name__=="__main__": main()
