"""Exercise native input and DP edge cases, including unsigned-char builds."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
CLUES_4 = "1 3 3 0 0 0 0 2 0 0 0 0 0 0 0 0"
CLUES_1 = "1 1 1 1"


@unittest.skipUnless(shutil.which("gcc"), "Requires the solver compiler")
class RobustnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        (ROOT / "scratch").mkdir(exist_ok=True)
        cls.tmp = tempfile.TemporaryDirectory(dir=ROOT / "scratch")
        cls.binary = Path(cls.tmp.name) / "solver"
        harness = Path(cls.tmp.name) / "harness"
        sources = sorted(str(p) for p in (ROOT / "src").glob("*.c"))
        flags = ["gcc", "-Wall", "-Wextra", "-Werror", "-O2", "-flto",
                 "-funsigned-char", "-I", str(ROOT / "src")]
        cls.compile(flags + sources + ["-o", str(cls.binary)])
        cls.compile(flags + [str(ROOT / "python_scripts/tests/c/robustness_harness.c"),
                             *(p for p in sources if not p.endswith("/main.c")),
                             "-o", str(harness)])
        result = subprocess.run([str(harness)], capture_output=True,
                                text=True, timeout=30)
        if result.returncode != 0:
            raise AssertionError(result.stderr)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "tmp"):
            cls.tmp.cleanup()

    @staticmethod
    def compile(command):
        result = subprocess.run(command, capture_output=True, text=True,
                                timeout=120)
        if result.returncode != 0:
            raise AssertionError(result.stderr)

    def solve(self, *args):
        return subprocess.run([str(self.binary), *args], capture_output=True,
                              text=True, timeout=30)

    def test_invalid_solution_limits(self):
        for invalid in ("", "-1", "+1", "2oops", "1.5",
                        "18446744073709551616", "18446744073709551615"):
            with self.subTest(limit=invalid):
                result = self.solve("-s", invalid, CLUES_4)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Error:", result.stderr)

    def test_positive_and_unlimited_counts(self):
        for count, wanted in ((1, 1), (2, 2), (0, 2)):
            with self.subTest(limit=count):
                result = self.solve("-s", str(count), CLUES_4)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f"Solutions found: {wanted}", result.stdout)
        unlimited = self.solve("-s", "0", CLUES_4)
        self.assertIn("Max solutions: 0", unlimited.stdout)
        grid_rows = [line for line in unlimited.stdout.splitlines()
                     if len(line.split()) == 4
                     and all(value in "1234" for value in line.split())]
        self.assertEqual(len(grid_rows), 4, unlimited.stdout)

    def test_one_by_one_with_and_without_limit(self):
        for args in ((CLUES_1,), ("-s", "0", CLUES_1)):
            with self.subTest(args=args):
                result = self.solve(*args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("Solutions found: 1", result.stdout)
                self.assertIn("\n1\n", result.stdout)


if __name__ == "__main__":
    unittest.main()
