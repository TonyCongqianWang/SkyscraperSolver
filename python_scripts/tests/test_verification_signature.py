"""Regression tests for deterministic node verification signatures."""
import contextlib
import hashlib
import io
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from python_scripts import verify_consistency as verify


class SignatureTests(unittest.TestCase):
    def test_signature_has_totals_and_order_sensitive_digest(self):
        counts = [7, 2, 11, 4]
        expected_hash = hashlib.sha256(b"7\n2\n11\n4\n").hexdigest()[:16]
        self.assertEqual(verify.verification_signature(counts),
                         f"24:2:11:{expected_hash}")
        self.assertNotEqual(verify.verification_signature(counts),
                            verify.verification_signature(list(reversed(counts))))

    def test_empty_run_is_rejected(self):
        with self.assertRaises(ValueError):
            verify.verification_signature([])

    def test_parallel_pass_preserves_dataset_order(self):
        instances = [(1, "first", 1), (2, "second", 1), (3, "third", 1)]
        counts = {"first": 9, "second": 3, "third": 15}
        barrier = threading.Barrier(3)

        def solver(binary, options, clue):
            barrier.wait(timeout=10)
            time.sleep({"first": 0.03, "second": 0.01, "third": 0}[clue])
            return {"solutions": 1, "nodes": counts[clue]}

        with patch.object(verify, "run_solver", side_effect=solver):
            with contextlib.redirect_stdout(io.StringIO()):
                passed, nodes = verify.run_pass(
                    "enumeration", instances, "solver", None, "-s 0", 3)
        self.assertTrue(passed)
        self.assertEqual(nodes, [9, 3, 15])

    def test_missing_nodes_fails_instead_of_signing(self):
        with patch.object(verify, "run_solver",
                          return_value={"solutions": 1, "nodes": None}):
            with contextlib.redirect_stdout(io.StringIO()):
                passed, nodes = verify.run_pass(
                    "enumeration", [(1, "clue", 1)], "solver", None, "-s 0", 1)
        self.assertFalse(passed)
        self.assertIsNone(nodes)

    def test_one_signature_per_dataset_not_per_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            clues = path / "clues.txt"
            expected = path / "expected.txt"
            clues.write_text("first\nsecond\n", encoding="utf-8")
            expected.write_text("1\n1\n", encoding="utf-8")

            def solver(binary, options, clue):
                return {"solutions": 1, "nodes": {"first": 6, "second": 4}[clue]}

            output = io.StringIO()
            with patch.object(verify, "run_solver", side_effect=solver):
                with contextlib.redirect_stdout(output):
                    passed = verify.verify_file(str(clues), str(expected),
                                                "solver", None, "-s 0", 2)
            self.assertTrue(passed)
            lines = [line.strip() for line in output.getvalue().splitlines()
                     if "Verification signature:" in line]
            self.assertEqual(lines, [
                f"Verification signature: {verify.verification_signature([6, 4])}"
            ])


if __name__ == "__main__":
    unittest.main()
