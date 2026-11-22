/* Independent controlled operation benchmark (not solver instrumentation).
 * Compile with production -O2 -flto and the actual C operation sources.
 * Operations are repeated inside a single CPU-clock interval so timer
 * overhead is amortized; a compiler memory barrier preserves side effects.
 * This is an experiment, NOT an automatically trusted cost model.
 */
#define _POSIX_C_SOURCE 200809L
#include "node_selection_cache.h"
#include "prune_check_constr.h"
#include "entropy.h"
#include <stdio.h>
#include <time.h>

static t_order_items g_source;
static t_order_items g_target;
static t_solver_state g_puzzle;
static t_node_state g_node;
static volatile unsigned long long g_sink;

static void escape_address(void *ptr)
{
    __asm__ __volatile__("" : : "g"(ptr) : "memory");
}

static double cpu_seconds(void)
{
    struct timespec t;
    if (clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t))
        return -1.0;
    return (double)t.tv_sec + (double)t.tv_nsec / 1e9;
}

static void emit(const char *section, int calls, int size,
                 double begin, double end)
{
    if (end <= begin)
        return;
    printf("WORK_BENCH v1 section=%s calls=%d volume=%d cpu_seconds=%.12f\n",
           section, calls, size * calls, end - begin);
}

static void bench_cache_copy(int count, int repeats)
{
    int i;
    double begin;
    double end;

    g_source.count = count;
    for (i = 0; i < count; ++i)
    {
        g_source.entries[i].cell_idx = i;
        g_source.meta[i].entropy_pos = i;
    }
    escape_address(&g_source);
    begin = cpu_seconds();
    for (i = 0; i < repeats; ++i)
    {
        copy_order_items(&g_target, &g_source);
        escape_address(&g_target);
        g_sink += (unsigned long long)g_target.entries[count - 1].cell_idx;
    }
    end = cpu_seconds();
    emit("cache_pair_copy_call", repeats, count, begin, end);
}

static void bench_index_copy(int size, int repeats)
{
    int i;
    int grid[9];
    int reversed[9];
    double begin;
    double end;

    for (i = 0; i < size; ++i)
        g_puzzle.constr_bounds.cur_c_pair.grid_indeces[i] = i;
    escape_address(&g_puzzle);
    begin = cpu_seconds();
    for (i = 0; i < repeats; ++i)
    {
        copy_indices(&g_puzzle, grid, reversed, size);
        escape_address(grid);
        escape_address(reversed);
        g_sink += (unsigned long long)grid[0];
    }
    end = cpu_seconds();
    emit("index_copy_call", repeats, size, begin, end);
}

static void bench_line_entropy(int size, int repeats)
{
    int i;
    double begin;
    double end;

    g_node.solver = &g_puzzle;
    g_puzzle.size = size;
    for (i = 0; i < size; ++i)
        g_node.domain.constrs.num_val_positions[0][i] = (char)(i % size + 1);
    escape_address(&g_node);
    begin = cpu_seconds();
    for (i = 0; i < repeats; ++i)
    {
        g_sink += (unsigned long long)compute_constr_entropy(
            &g_node, 0, size);
        escape_address(&g_node);
    }
    end = cpu_seconds();
    emit("line_score", repeats, size, begin, end);
}

int main(int argc, char **argv)
{
    int repeats;
    int sizes[] = {7, 8, 9};
    int count;
    int i;

    if (argc != 2 || sscanf(argv[1], "%d", &repeats) != 1
        || repeats < 1000 || repeats > 2000000)
        return 2;
    for (count = 4; count <= 256; count *= 2)
        bench_cache_copy(count, repeats);
    for (i = 0; i < 3; ++i)
    {
        bench_index_copy(sizes[i], repeats);
        bench_line_entropy(sizes[i], repeats);
    }
    if (g_sink == 0xFFFFFFFFFFFFFFFFULL)
        fprintf(stderr, "sink=%llu\n", g_sink);
    return 0;
}
