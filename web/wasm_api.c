/* Minimal synchronous C API for the WebAssembly worker.
 * Inputs use the same space-separated clue/grid format as the native CLI.
 * Result: "count|nodes|size|first-solution-row-major-digits", or "ERR:reason".
 * The result is owned by this module and overwritten by the next invocation.
 */
#include "argument_parsing.h"
#include "puzzle_solver.h"
#include "solution_storage.h"
#include <stdio.h>
#include <string.h>

static t_solver_state web_puzzle;
static char result[512];

const char *solve_web(const char *clues, const char *grid, int max_solutions)
{
    char limit[24];
    char *argv[5];
    int argc;
    int i;
    size_t used;

    if (!clues || !grid || max_solutions < 1 || max_solutions > 100) {
        return "ERR:Invalid arguments (solution limit must be 1..100)";
    }
    memset(&web_puzzle, 0, sizeof(web_puzzle));
    snprintf(limit, sizeof(limit), "%d", max_solutions);
    argv[0] = "skyscraper_solver";
    argv[1] = "-s";
    argv[2] = limit;
    argv[3] = (char *)clues;
    argv[4] = (char *)grid;
    argc = (grid[0] ? 5 : 4);
    if (init_puzzle_from_argv(&web_puzzle, argc, argv) != 0) {
        free_solution_storage(&web_puzzle);
        return "ERR:Invalid clues or grid (see format instructions)";
    }
    solve_puzzle(&web_puzzle, -1);
    used = (size_t)snprintf(result, sizeof(result), "%llu|%llu|%d|",
        (unsigned long long)web_puzzle.solutions_found,
        (unsigned long long)web_puzzle.nodes_visited, web_puzzle.size);
    if (web_puzzle.solutions_found > 0 && web_puzzle.solutions) {
        for (i = 0; i < web_puzzle.squared_size && used + 2 < sizeof(result); ++i)
            result[used++] =
                (char)('0' + web_puzzle.solutions[0].domain.vals[i]);
    }
    result[used] = '\0';
    free_solution_storage(&web_puzzle);
    return result;
}
