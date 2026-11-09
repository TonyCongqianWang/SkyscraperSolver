"""Check nesting-dependent tier depths and zero-depth skipping."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class LookaheadDepthTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("gcc"), "Requires the solver compiler")
    def test_production_and_ci_depth_matrices(self):
        (ROOT / "scratch").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "scratch") as temporary:
            sources = sorted(str(path) for path in (ROOT / "src").glob("*.c")
                             if path.name not in ("main.c", "lookahead_depth.c"))
            harness = ROOT / "python_scripts/tests/c/lookahead_depth_harness.c"
            for ci in (False, True):
                with self.subTest(ci=ci):
                    config = (ROOT / "python_scripts/tests/config/lookahead_depth_ci.c"
                              if ci else ROOT / "src/lookahead_depth.c")
                    binary = Path(temporary) / f"depth_test_{ci}"
                    command = ["gcc", "-Wall", "-Wextra", "-Werror", "-O2", "-flto",
                               "-I", str(ROOT / "src"), str(harness), *sources,
                               str(config), "-o", str(binary)]
                    if ci:
                        command.append("-DCI_LOOKAHEAD_DEPTH")
                    compiled = subprocess.run(command, capture_output=True, text=True)
                    self.assertEqual(compiled.returncode, 0, compiled.stderr)
                    result = subprocess.run([str(binary)], capture_output=True,
                                            text=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
