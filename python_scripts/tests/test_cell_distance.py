"""Compile the real C distance implementation and check all supported sizes."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

HARNESS = r'''
#include <assert.h>
#include "cell_distance.c"

static void check_cell(int size, int row, int col)
{
    int a = row < size - 1 - row ? row : size - 1 - row;
    int b = col < size - 1 - col ? col : size - 1 - col;
    int low = a < b ? a : b;
    int high = a > b ? a : b;
    int score = (size + 1) * (size + 1) - low * (size + 1) - high;
    int r = row;
    int c = col;
    int turn;
    int next;

    assert(get_edge_distance(row, size) == a);
    assert(get_edge_distance(col, size) == b);
    for (turn = 0; turn < 4; turn++)
    {
        assert(get_cell_dist_val(r * size + c, size) == score);
        assert(get_cell_dist_val(r * size + size - 1 - c, size) == score);
        next = c;
        c = size - 1 - r;
        r = next;
    }
}

static void check_order(int size)
{
    static t_puzzle puzzle;
    int seen[MAX_CELL_COUNT] = {0};
    int i;
    int idx;
    int previous = (size + 1) * (size + 1) + 1;
    int score;

    puzzle.squared_size = size * size;
    init_cell_distance_order(&puzzle, size);
    for (i = 0; i < size * size; i++)
    {
        idx = puzzle.cell_distance_order[i];
        assert(idx >= 0 && idx < size * size && !seen[idx]);
        seen[idx] = 1;
        score = get_cell_dist_val(idx, size);
        assert(score <= previous);
        if (i > 0 && score == previous)
            assert(idx > puzzle.cell_distance_order[i - 1]);
        previous = score;
    }
}

int main(void)
{
    int size;
    int row;
    int col;

    for (size = 4; size <= MAX_SIZE; size++)
    {
        for (row = 0; row < size; row++)
            for (col = 0; col < size; col++)
                check_cell(size, row, col);
        check_order(size);
    }
    return 0;
}
'''


class CellDistanceTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('gcc'), 'Requires the solver compiler')
    def test_real_c_distances_scores_and_stable_order(self):
        (ROOT / 'scratch').mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=ROOT / 'scratch') as temporary:
            directory = Path(temporary)
            source = directory / 'test.c'
            binary = directory / 'test_distance'
            source.write_text(HARNESS)
            subprocess.run(['gcc', '-Wall', '-Wextra', '-Werror', '-I', str(ROOT / 'src'),
                            str(source), '-o', str(binary)], check=True, capture_output=True)
            subprocess.run([str(binary)], check=True, capture_output=True)


if __name__ == '__main__':
    unittest.main()
