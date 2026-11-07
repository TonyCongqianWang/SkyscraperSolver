"""Keep the mixed-clue size-9 verification fixture reproducible."""
import json
from pathlib import Path
import shlex
from unittest.mock import Mock, patch

import pytest

from python_scripts import verify_consistency as verify

ROOT = Path(__file__).resolve().parents[2]


def test_default_verification_includes_size9():
    with patch.object(verify.sys, "argv", ["verify_consistency.py"]), \
         patch.object(verify.subprocess, "run"), \
         patch.object(verify, "run_solver", side_effect=[
             {"solutions": n} for n in (2, 1, 2, 2)]), \
         patch.object(verify, "verify_file", return_value=True) as check:
        with pytest.raises(SystemExit) as result:
            verify.main()
        assert result.value.code == 0
    assert any(call.args[:2] == (
        "benchmark_sets/benchmarkSet9_minimal20.txt",
        "benchmark_sets/_num_solutions_benchmarkSet9_minimal20.txt")
        for call in check.call_args_list)


def test_mixed_puzzle_arguments_are_preserved():
    process = Mock(returncode=0)
    process.communicate.return_value = ("Solutions found: 2\nNodes visited: 5\n", "")
    for line, args in [('"1 0 0 0" "1"', ["1 0 0 0", "1"]),
                       ('"1 0 0 0"', ["1 0 0 0"]),
                       ("1 0 0 0", ["1 0 0 0"])]:
        with patch.object(verify.subprocess, "Popen", return_value=process) as popen:
            assert verify.run_solver("solver", "-s 0", line)["solutions"] == 2
        assert popen.call_args.args[0] == ["solver", "-s", "0", *args]


@pytest.mark.parametrize("size", [7, 8, 9])
def test_fixture_matches_minimal_sources(size):
    directory = ROOT / "benchmark_sets"
    name = f"benchmarkSet{size}_" + ("minimal20" if size == 9 else "python20")
    rows = (directory / f"{name}.txt").read_text().splitlines()
    counts = [int(v) for v in (directory / f"_num_solutions_{name}.txt").read_text().splitlines()]
    provenance = json.loads((directory / f"{name}.json").read_text())
    bank = json.loads((ROOT / provenance["source"]).read_text())
    sources = {p["id"]: p for g in bank["groups"] for p in g["puzzles"]}
    assert len(rows) == len(counts) == len(provenance["instances"]) == 20
    assert len(set(rows)) == 20
    assert len({p["source_id"].split("-p")[0] for p in provenance["instances"]}) == 20
    for row, count, record in zip(rows, counts, provenance["instances"]):
        edges, givens = [list(map(int, arg.split())) for arg in shlex.split(row)]
        source = sources[record["source_id"]]
        assert len(edges) == 4 * size and len(givens) == size * size
        assert givens == source["givens"]
        removed = record["removed_clue_indices"]
        assert len(removed) == 1
        assert [i for i, (a, b) in enumerate(zip(source["clues"], edges)) if a != b] == removed
        assert all(source["clues"][i] > 0 and edges[i] == 0 for i in removed)
        assert count == record["solutions"] and 2 <= count <= 4
