/* Controlled CPU-time measurements of the C operations underlying work counters.
 * The same optimized solver sources are linked; timers surround many repeated
 * operations. This harness intentionally varies call counts and data lengths.
 */
#define _POSIX_C_SOURCE 200809L
#include "node_selection_cache.h"
#include "prune_check_constr.h"
#include "grid_availability.h"
#include "cell_bounds.h"
#include "line_order.h"
#include "entropy.h"
#include "constraint_checking.h"
#include "constraint_selection.h"
#include "constraint_update.h"
#include "grid_manipulation.h"
#include "grid_interface.h"
#include "check_node_validity.h"
#include "push_dirty_constraints.h"
#include "node_selection_eval.h"
#include "selectivity.h"
#include <limits.h>
#include <stdio.h>
#include <time.h>
#include <string.h>

static t_solver_state puzzle;
static t_node_state node;
static t_order_items source;
static t_order_items target;
static t_order_state saved_state;
static t_line_order line_a;
static t_line_order line_b;
static volatile unsigned long long sink;

static void barrier(void *p)
{
    __asm__ __volatile__("" : : "g"(p) : "memory");
}

static double clock_seconds(void)
{
    struct timespec t;
    if (clock_gettime(CLOCK_PROCESS_CPUTIME_ID, &t) != 0)
        return -1.0;
    return (double)t.tv_sec + (double)t.tv_nsec / 1e9;
}

static void emit_individual(const char *name, int round, int units,
                            double start)
{
    double duration = clock_seconds() - start;
    if (duration <= 0.0)
        duration = 0.0;
    printf("WORK_BENCH v1 kind=individual counter=%s round=%d"
           " units=%d cpu_seconds=%.12f\n",
           name, round, units, duration);
}

static void emit_affine(const char *name, int round, int calls, int volume,
                         double start)
{
    double duration = clock_seconds() - start;
    if (duration <= 0.0)
        duration = 0.0;
    printf("WORK_BENCH v1 kind=affine section=%s round=%d calls=%d"
           " volume=%d cpu_seconds=%.12f\n",
           name, round, calls, volume, duration);
}

static void prepare(int size)
{
    int i;
    puzzle.size = size;
    puzzle.squared_size = size * size;
    node.solver = &puzzle;
    node.size = size;
    node.order_cache = &puzzle.order_stack.orders[0];
    puzzle.cur_node = &node;
    puzzle.order_stack.top_idx = 1;
    line_a.count = 2 * size;
    for (i = 0; i < size * size; i++)
    {
        puzzle.cell_distance_order[i] = i;
        node.domain.valid_val_bmps[i] = (1 << size) - 1;
        node.domain.vals[i] = 0;
        node.domain.num_cell_vals[i] = size;
    }
    for (i = 0; i < 2 * size; i++)
    {
        line_a.entries[i].constr_idx = i;
        line_a.entries[i].entropy = i;
    }
    for (i = 0; i < size; i++)
        node.domain.constrs.num_val_positions[0][i] = i + 1;
    for (i = 0; i < 256; i++)
    {
        source.entries[i].cell_idx = i % (size * size);
        source.entries[i].cell_val = i % size + 1;
        source.entries[i].score = (double)(i % 17);
        source.meta[i].entropy_pos = i % 7;
    }
    saved_state.build_depth = size;
    barrier(&node);
    barrier(&source);
}

static void benchmark_affine(int repeats, int round)
{
    int sizes[] = {0, 4, 16, 64, 256};
    int n, i, k;
    double start;
    int idx[9] = {0}, rev[9] = {0};

    for (k = 0; k < 5; k++)
    {
        n = sizes[k];
        source.count = n;
        start = clock_seconds();
        for (i = 0; i < repeats; i++)
        {
            copy_order_items(&target, &source);
            barrier(&target);
            sink += (unsigned long long)target.count;
        }
        emit_affine("cache_pair_copy_call", round, repeats,
                    repeats * n, start);
        if (n == 0)
            emit_individual("cache_pair_copy_call", round, repeats, start);
    }
    for (n = 0; n <= 9; n += 3)
    {
        start = clock_seconds();
        for (i = 0; i < repeats; i++)
        {
            copy_indices(&puzzle, idx, rev, n);
            barrier(idx);
            barrier(rev);
            sink += (unsigned long long)idx[0];
        }
        emit_affine("index_copy_call", round, repeats,
                    repeats * n, start);
        if (n == 0)
            emit_individual("index_copy_call", round, repeats, start);
    }
    for (n = 7; n <= 9; n++)
    {
        start = clock_seconds();
        for (i = 0; i < repeats; i++)
        {
            sink += (unsigned long long)compute_constr_entropy(&node, 0, n);
            barrier(&node);
        }
        emit_affine("line_score", round, repeats, repeats * n, start);
    }
}

static void bench_setup(int repeats, int round)
{
    int i;
    double start;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        node.domain.vals[i % 49] = 0;
        node.domain.valid_val_bmps[i % 49] = 0x7f;
        update_cell_bounds(&node, i % 49);
        node.domain.num_cell_vals[i % 49] = node.size;
        barrier(&node);
    }
    emit_individual("setup_cell", round, repeats, start);
    /* Count full cache-build checks, including valid transitions. */
    {
        int runs = repeats / 343;
        int units = runs * 343;
        if (runs < 1)
            runs = 1, units = 343;
        start = clock_seconds();
        for (i = 0; i < runs; i++)
        {
            collect_cache_entries(&puzzle, &puzzle.order_stack.orders[0], NULL);
            barrier(&puzzle.order_stack.orders[0]);
            sink += (unsigned long long)puzzle.order_stack.orders[0].items.count;
        }
        emit_individual("cache_build_candidate", round, units, start);
    }
}

static void bench_copies(int repeats, int round)
{
    int i;
    double start;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        puzzle.order_stack.orders[1].state = saved_state;
        barrier(&puzzle.order_stack.orders[1].state);
        sink += (unsigned long long)saved_state.build_depth;
    }
    emit_individual("cache_state_copy", round, repeats, start);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        line_b = line_a;
        barrier(&line_b);
        sink += (unsigned long long)line_b.count;
    }
    emit_individual("line_copy", round, repeats, start);
}

static void bench_compact(int repeats, int round)
{
    int i, cell, value;
    double start;
    t_node_transition *entries = source.entries;
    t_transition_meta *meta = source.meta;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        cell = i % 49;
        value = i % 7 + 1;
        sink += (unsigned long long)(
            is_cell_empty(&node, cell) &&
            is_valid_value(&node, cell, value));
        barrier(&node);
    }
    emit_individual("compact_check", round, repeats, start);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        entries[1] = entries[i % 32 + 2];
        meta[1] = meta[i % 32 + 2];
        barrier(&entries[1]);
        sink += (unsigned long long)entries[1].cell_idx;
    }
    emit_individual("compact_move", round, repeats, start);
}

static void bench_sort(int repeats, int round)
{
    int i;
    double start;
    t_line_priority line_dst;
    t_node_transition transition_dst;
    t_transition_meta meta_dst;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        sink += (unsigned long long)(
            line_a.entries[i % 14].entropy > line_a.entries[(i + 1) % 14].entropy);
        barrier(&line_a);
    }
    emit_individual("line_compare", round, repeats, start);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        line_dst = line_a.entries[i % 14];
        barrier(&line_dst);
        sink += (unsigned long long)line_dst.constr_idx;
    }
    emit_individual("line_shift", round, repeats, start);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        sink += (unsigned long long)(
            source.entries[i % 64].score < source.entries[(i + 1) % 64].score);
        barrier(&source);
    }
    emit_individual("transition_compare", round, repeats, start);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        transition_dst = source.entries[i % 64];
        meta_dst = source.meta[i % 64];
        barrier(&transition_dst);
        barrier(&meta_dst);
        sink += (unsigned long long)transition_dst.cell_idx;
    }
    emit_individual("transition_shift", round, repeats, start);
}


/* Repeated genuine clue-bound checks with independently varied line size.
 * The first point measures call overhead, with zero scanned cells.
 */
static void bench_constraint_affine(int repeats, int round)
{
    int n, i;
    double start;
    t_constraint_bounds *bounds = &puzzle.constr_bounds;

    for (n = 0; n <= 9; n += 3)
    {
        puzzle.size = n;
        node.size = n;
        bounds->size = n;
        bounds->cur_c_pair.fwd_val = n > 0 ? n : 1;
        bounds->is_reverse = 0;
        for (i = 0; i < n; i++)
        {
            bounds->cur_c_pair.grid_indeces[i] = i;
            node.domain.vals[i] = 0;
            node.domain.valid_val_bmps[i] = (1 << n) - 1;
            update_cell_bounds(&node, i);
        }
        start = clock_seconds();
        for (i = 0; i < repeats; i++)
        {
            reset_constraint_bounds(&puzzle);
            sink += (unsigned long long)check_active_constr(&puzzle);
            barrier(bounds);
        }
        emit_affine("constraint_check_call", round, repeats,
                    repeats * n, start);
    }
    prepare(7);
}

static void bench_constraint_subtasks(int repeats, int round)
{
    int i;
    double start;

    puzzle.constr_bounds.size = 7;
    puzzle.constr_bounds.cur_c_pair.fwd_val = 7;
    node.domain.vals[0] = 0;
    node.domain.valid_val_bmps[0] = 0x7f;
    update_cell_bounds(&node, 0);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        reset_constraint_bounds(&puzzle);
        sink += (unsigned long long)update_constr_bounds(&puzzle, 0);
        barrier(&puzzle.constr_bounds);
    }
    emit_individual("constraint_check_unset_cell", round, repeats, start);
    puzzle.grid_constr_map[0][0] = 0;
    puzzle.grid_constr_map[0][1] = 1;
    puzzle.constraint_pairs[0].fwd_val = 1;
    puzzle.constraint_pairs[0].bwd_val = 0;
    puzzle.constraint_pairs[1].fwd_val = 0;
    puzzle.constraint_pairs[1].bwd_val = 0;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        node.dirty_constrs.count = 0;
        node.dirty_constrs.in_stack_bmp = 0;
        push_dirty_constraints(&node, 0);
        barrier(&node.dirty_constrs);
        sink += (unsigned long long)node.dirty_constrs.count;
    }
    emit_individual("dirty_constraint_enqueue", round, repeats, start);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        node.dirty_constrs.count = 1;
        node.dirty_constrs.entries[0] = 0;
        node.dirty_constrs.in_stack_bmp = 1;
        check_node_validity(&puzzle, g_check_none);
        barrier(&node.dirty_constrs);
        sink += (unsigned long long)node.dirty_constrs.count;
    }
    emit_individual("dirty_constraint_entry", round, repeats, start);
    node.domain.is_invalid = 1;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        set_value_invalid_internal(&node, 0, 1);
        barrier(&node);
    }
    emit_individual("domain_invalidation_attempt", round, repeats, start);
    node.domain.is_invalid = 0;
    node.size = 9;
    node.domain.valid_val_bmps[0] = 0x10;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        update_cell_bounds(&node, 0);
        barrier(&node);
    }
    emit_individual("cell_bound_skip", round, 8 * repeats, start);
    prepare(7);
}

static void bench_cache_traversals(int repeats, int round)
{
    int i;
    double start;
    t_node_transition next;
    t_node_select_config config;
    t_node_order *cache = &puzzle.order_stack.orders[0];

    for (i = 0; i < 49; i++)
        node.domain.vals[i] = 1;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        collect_cache_entries(&puzzle, cache, NULL);
        barrier(cache);
        sink += (unsigned long long)cache->items.count;
    }
    emit_individual("cache_build_cell_scan", round, 49 * repeats, start);
    cache->items.count = 16;
    for (i = 0; i < 16; i++)
    {
        cache->items.entries[i].cell_idx = i;
        cache->items.entries[i].cell_val = 1;
    }
    config.selectivity = SELECTIVITY_VALUE_SET;
    next.cell_idx = -1;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        next.cell_idx = -1;
        get_next_from_cache(&puzzle, &next, &config);
        barrier(cache);
    }
    emit_individual("cache_next_scan", round, 16 * repeats, start);
    next = cache->items.entries[15];
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        next = cache->items.entries[15];
        get_next_from_cache(&puzzle, &next, &config);
        barrier(cache);
    }
    emit_individual("cache_resume_scan", round, 16 * repeats, start);
    prepare(9);
    node.domain.valid_val_bmps[0] = 0x100;
    node.domain.cell_bounds[0] = (char)0x91;
    next.cell_idx = 0;
    next.cell_val = 1;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        next.cell_val = 1;
        sink += (unsigned long long)set_next_valid_val(&puzzle, &next);
        barrier(&next);
    }
    emit_individual("next_value_scan", round, 9 * repeats, start);
    prepare(7);
}


static void bench_prune_line_scan(int repeats, int round)
{
    int i;
    double start;
    t_constr_limits limits;
    t_line_order *order = &puzzle.line_order_stack.orders[0];

    prepare(7);
    order->count = 14;
    for (i = 0; i < order->count; ++i)
    {
        order->entries[i].constr_idx = i;
        puzzle.constraint_pairs[i].fwd_val = 0;
        puzzle.constraint_pairs[i].bwd_val = 0;
    }
    limits.min_entropy = 0.0;
    limits.max_entropy = 1.0;
    limits.global_min_entropy = INT_MAX;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        prune_check_constr(&puzzle, SELECTIVITY_NONE, &limits);
        barrier(order);
    }
    emit_individual("prune_line_scan", round, 14 * repeats, start);
}

static void bench_dp_scans(int repeats, int round)
{
    int i, k, m, scanned;
    int domains[9];
    t_dp_tables dp;
    t_prune_args args;
    double start;

    prepare(7);
    for (i = 0; i < 7; i++)
    {
        domains[i] = 0x7f;
        node.domain.vals[i] = 0;
        node.domain.valid_val_bmps[i] = 0;
    }
    init_dp_tables(&dp, 7);
    fill_pref_dp(&dp, domains, 7);
    scanned = 0;
    for (k = 0; k < 7; k++)
        for (m = 0; m <= 7; m++)
            if (dp.pref_max[k][m] != -1)
                scanned += 7;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        init_dp_tables(&dp, 7);
        fill_pref_dp(&dp, domains, 7);
        barrier(&dp);
    }
    emit_individual("dp_prefix_candidate_scan", round,
                    scanned * repeats, start);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        init_dp_tables(&dp, 7);
        fill_suff_dp(&dp, domains, 7);
        barrier(&dp);
    }
    emit_individual("dp_suffix_candidate_scan", round,
                    7 * 8 * 7 * repeats, start);
    args.solver = &puzzle;
    args.state = &node;
    args.size = 7;
    args.dp = &dp;
    for (i = 0; i < 7; i++)
        args.grid_indices = puzzle.constr_bounds.cur_c_pair.grid_indeces;
    for (i = 0; i < 7; i++)
        puzzle.constr_bounds.cur_c_pair.grid_indeces[i] = i;
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        sink += (unsigned long long)prune_candidates(&args);
        barrier(&node);
    }
    emit_individual("dp_prune_value_scan", round, 49 * repeats, start);
}

int main(int argc, char **argv)
{
    int repeats, round;
    if (argc != 3 || sscanf(argv[1], "%d", &repeats) != 1 ||
        sscanf(argv[2], "%d", &round) != 1 || repeats < 1000 ||
        repeats > 2000000 || round < 0)
        return 2;
    prepare(7);
    benchmark_affine(repeats, round);
    bench_setup(repeats, round);
    bench_copies(repeats, round);
    bench_compact(repeats, round);
    bench_sort(repeats, round);
    bench_constraint_affine(repeats, round);
    bench_constraint_subtasks(repeats, round);
    bench_cache_traversals(repeats, round);
    bench_prune_line_scan(repeats, round);
    bench_dp_scans(repeats, round);
    if (sink == 0xFFFFFFFFFFFFFFFFULL)
        fprintf(stderr, "sink=%llu\n", sink);
    return 0;
}
