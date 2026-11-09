"""Check nesting-dependent tier depths and zero-depth skipping."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]


class LookaheadDepthTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("gcc"), "Requires the solver compiler")
    def test_depth_matrices_and_probe_sides(self):
        (ROOT / "scratch").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / "scratch") as temporary:
            sources = sorted(str(path) for path in (ROOT / "src").glob("*.c")
                             if path.name not in ("main.c", "lookahead_depth.c"))
            harness = ROOT / "python_scripts/tests/c/lookahead_depth_harness.c"
            for name in ("production", "ci", "marking"):
                with self.subTest(config=name):
                    config = (ROOT / "src/lookahead_depth.c" if name == "production"
                              else ROOT / f"python_scripts/tests/config/lookahead_depth_{name}.c")
                    binary = Path(temporary) / f"depth_test_{name}"
                    command = ["gcc", "-Wall", "-Wextra", "-Werror", "-O2",
                               "-I", str(ROOT / "src"), str(harness), *sources,
                               str(config), "-o", str(binary),
                               "-Wl,--wrap=probe_assumption", "-Wl,--wrap=probe_exclusion"]
                    if name != "production":
                        command.append(f"-D{name.upper()}_LOOKAHEAD_DEPTH")
                    compiled = subprocess.run(command, capture_output=True, text=True)
                    self.assertEqual(compiled.returncode, 0, compiled.stderr)
                    result = subprocess.run([str(binary)], capture_output=True,
                                            text=True, timeout=30)
                    self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
