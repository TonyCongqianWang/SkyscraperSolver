"""Failures in reference solver verification must fail CI within its budget."""
from pathlib import Path
import subprocess
from unittest.mock import Mock, patch

import pytest

from python_solver import verify


def fixture_files(tmp_path, rows='"0 0 0 0" "0"\n', counts="1\n"):
    puzzles = tmp_path / "puzzles.txt"
    expected = tmp_path / "counts.txt"
    puzzles.write_text(rows)
    expected.write_text(counts)
    return puzzles, expected


def test_explicit_backend_exhaustive_count_and_mixed_arguments(tmp_path):
    files = fixture_files(tmp_path)
    result = Mock(returncode=0, stdout="Total Unique Solutions Found: 1\n", stderr="")
    with patch.object(verify.subprocess, "run", return_value=result) as run:
        verify.verify_dataset("z3", *files)
    command = run.call_args.args[0]
    assert command[-6:] == ["-b", "z3", "-s", "0", "0 0 0 0", "0"]
    assert run.call_args.kwargs["timeout"] == 10


@pytest.mark.parametrize("result", [
    Mock(returncode=0, stdout="Total Unique Solutions Found: 2\n", stderr=""),
    Mock(returncode=0, stdout="--- END_OF_INSTANCE ---\n", stderr=""),
    Mock(returncode=1, stdout="Total Unique Solutions Found: 1\n", stderr="broken"),
])
def test_wrong_missing_or_failed_count_is_rejected(tmp_path, result):
    with patch.object(verify.subprocess, "run", return_value=result):
        with pytest.raises(RuntimeError, match="row 1"):
            verify.verify_dataset("cpsat", *fixture_files(tmp_path))


def test_case_timeout_is_reported(tmp_path):
    with patch.object(verify.subprocess, "run", side_effect=subprocess.TimeoutExpired("solver", 10)):
        with pytest.raises(RuntimeError, match="row 1: exceeded 10.0s"):
            verify.verify_dataset("z3", *fixture_files(tmp_path))


def test_remaining_total_budget_caps_subprocess(tmp_path):
    result = Mock(returncode=0, stdout="Total Unique Solutions Found: 1\n", stderr="")
    with patch.object(verify.time, "monotonic", return_value=100), \
         patch.object(verify.subprocess, "run", return_value=result) as run:
        verify.verify_dataset("z3", *fixture_files(tmp_path), deadline=102)
    assert run.call_args.kwargs["timeout"] == 2


def test_exhausted_total_budget_starts_no_process(tmp_path):
    with patch.object(verify.time, "monotonic", return_value=100), \
         patch.object(verify.subprocess, "run") as run:
        with pytest.raises(RuntimeError, match="Total verification time budget"):
            verify.verify_dataset("z3", *fixture_files(tmp_path), deadline=99)
    run.assert_not_called()


def test_mismatched_fixture_lengths_are_rejected(tmp_path):
    with pytest.raises(ValueError, match="mismatched"):
        verify.verify_dataset("z3", *fixture_files(tmp_path, counts="1\n2\n"))
