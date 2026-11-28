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
#include "node_selection_score.h"
#include "transition_scoring.h"
#include "solution_storage.h"
#include "selectivity.h"
#include "work_instrumentation.h"
#include <limits.h>
#include <stdio.h>
#include <time.h>
#include <string.h>
#include <stdlib.h>

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

/* The normal timing binary stays uninstrumented. A second, instrumented
 * run checks actual loop counts before accepting the timing measurements.
 */
static void check_work_units(const char *label, t_work_counter counter,
                             unsigned long long before,
                             unsigned long long expected)
{
#ifdef WORK_INSTRUMENTED
    unsigned long long after = work_get(counter);
    if (after < before || after - before != expected)
    {
        fprintf(stderr, "Work unit mismatch for %s: expected %llu, got %llu\n",
                label, expected, after >= before ? after - before : 0ULL);
        exit(3);
    }
#else
    (void)label;
    (void)counter;
    (void)before;
    (void)expected;
#endif
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
        if (n == 0)
        {
            unsigned long long before = work_get(WORK_CONSTRAINT_CHECK_CALL);
            unsigned long long cells = work_get(WORK_CONSTRAINT_CHECK_CELL);
            start = clock_seconds();
            for (i = 0; i < repeats; i++)
            {
                sink += (unsigned long long)check_active_constr(&puzzle);
                barrier(bounds);
            }
            emit_individual("constraint_check_call", round, repeats, start);
            check_work_units("constraint_check_call", WORK_CONSTRAINT_CHECK_CALL,
                             before, repeats);
            check_work_units("constraint_check_zero_cells",
                             WORK_CONSTRAINT_CHECK_CELL, cells, 0);
        }
    }
    prepare(7);
}

/* Paired timing: real assignment versus its independently counted nested
 * invalidations and queue operations. Both paths include the same node reset.
 * The residual estimates assignment-only bookkeeping; the gross and nested
 * CPU times are retained because the residual can be near zero or noisy.
 */
static void bench_assignment(int repeats, int round)
{
    int i, j;
    double start, gross_seconds, nested_seconds, net_seconds;
    unsigned long long before_assignment, before_attempts, before_invalids;
    unsigned long long before_enqueue;
    t_node_state clean;

    prepare(7);
    node.domain.num_unset = 49;
    node.domain.is_invalid = 0;
    node.domain.is_complete = 0;
    node.domain.remaining_entropy = compute_max_entropy(7);
    node.dirty_constrs.count = 0;
    node.dirty_constrs.in_stack_bmp = 0;
    for (i = 0; i < 49; i++)
    {
        puzzle.grid_constr_map[i][0] = i % 7;
        puzzle.grid_constr_map[i][1] = 7 + i / 7;
    }
    for (i = 0; i < 14; i++)
    {
        puzzle.constraint_pairs[i].fwd_val = 0;
        puzzle.constraint_pairs[i].bwd_val = 0;
        for (j = 0; j < 7; j++)
            node.domain.constrs.num_val_positions[i][j] = 7;
    }
    puzzle.constraint_pairs[0].fwd_val = 1;
    puzzle.constraint_pairs[7].fwd_val = 1;
    clean = node;

    /* Control: same 18 actual invalidations and two enqueues, without the
     * successful assignment itself. Leave the assigned cell unset, but its
     * candidate value and adjacent domain state are otherwise identical.
     */
    before_assignment = work_get(WORK_ASSIGNMENT);
    before_attempts = work_get(WORK_DOMAIN_INVALIDATION_ATTEMPT);
    before_invalids = work_get(WORK_DOMAIN_INVALIDATION);
    before_enqueue = work_get(WORK_DIRTY_CONSTRAINT_ENQUEUE);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        node = clean;
        /* The assigned cell is already occupied in the real path.
         * Replicate that state without calling the assignment function:
         * otherwise the last invalidation would trigger forced assignment.
         */
        node.domain.vals[0] = 1;
        for (j = 2; j <= 7; j++)
            set_value_invalid_internal(&node, 0, j);
        for (j = 1; j < 7; j++)
            set_value_invalid_internal(&node, j * 7, 1);
        for (j = 1; j < 7; j++)
            set_value_invalid_internal(&node, j, 1);
        push_dirty_constraints(&node, 0);
        barrier(&node);
        sink += (unsigned long long)node.domain.num_unset;
    }
    nested_seconds = clock_seconds() - start;
    if (node.domain.is_invalid || node.dirty_constrs.count != 2)
    {
        fprintf(stderr, "Nested assignment control invalid state\n");
        exit(3);
    }
    check_work_units("nested_control_no_assignment", WORK_ASSIGNMENT,
                     before_assignment, 0);
    check_work_units("nested_control_invalidation_attempts",
                     WORK_DOMAIN_INVALIDATION_ATTEMPT, before_attempts,
                     18ULL * (unsigned long long)repeats);
    check_work_units("nested_control_domain_invalidations",
                     WORK_DOMAIN_INVALIDATION, before_invalids,
                     18ULL * (unsigned long long)repeats);
    check_work_units("nested_control_dirty_enqueues",
                     WORK_DIRTY_CONSTRAINT_ENQUEUE, before_enqueue,
                     2ULL * (unsigned long long)repeats);

    before_assignment = work_get(WORK_ASSIGNMENT);
    before_attempts = work_get(WORK_DOMAIN_INVALIDATION_ATTEMPT);
    before_invalids = work_get(WORK_DOMAIN_INVALIDATION);
    before_enqueue = work_get(WORK_DIRTY_CONSTRAINT_ENQUEUE);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        node = clean;
        set_grid_val_internal(&node, 0, 1, 0);
        barrier(&node);
        sink += (unsigned long long)node.domain.vals[0];
    }
    gross_seconds = clock_seconds() - start;
    if (node.domain.vals[0] != 1 || node.domain.num_unset != 48
        || node.domain.is_invalid || node.dirty_constrs.count != 2)
    {
        fprintf(stderr, "Assignment microbenchmark invalid final state\n");
        exit(3);
    }
    check_work_units("assignment", WORK_ASSIGNMENT,
                     before_assignment, (unsigned long long)repeats);
    check_work_units("assignment_invalidation_attempts",
                     WORK_DOMAIN_INVALIDATION_ATTEMPT, before_attempts,
                     18ULL * (unsigned long long)repeats);
    check_work_units("assignment_domain_invalidations",
                     WORK_DOMAIN_INVALIDATION, before_invalids,
                     18ULL * (unsigned long long)repeats);
    check_work_units("assignment_dirty_enqueues",
                     WORK_DIRTY_CONSTRAINT_ENQUEUE, before_enqueue,
                     2ULL * (unsigned long long)repeats);
    net_seconds = gross_seconds - nested_seconds;
    printf("WORK_BENCH v1 kind=individual counter=assignment round=%d"
           " units=%d cpu_seconds=%.12f gross_cpu_seconds=%.12f"
           " nested_cpu_seconds=%.12f timing_scope=paired_residual"
           " nested_invalidation_attempts_per_unit=18"
           " nested_domain_invalidations_per_unit=18"
           " nested_dirty_enqueues_per_unit=2\n",
           round, repeats, net_seconds, gross_seconds, nested_seconds);
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

/* Vary initialization volume and update density independently. The suffix
 * scan count is fixed at size * (size + 1) * size for every density. */
static void bench_dp_affine(int repeats, int round)
{
    t_dp_tables dp;
    int domains[9];
    int n, i, j, density, writes, scans, updates;
    double start;
    unsigned long long before_call, before_volume;

    for (n = 0; n <= 9; n += 3)
    {
        writes = 4 * (n + 1) * (n + 1) + 2 + 2 * (n + 1);
        before_call = work_get(WORK_DP_INIT_CALL);
        before_volume = work_get(WORK_DP_INIT_WRITE);
        start = clock_seconds();
        for (i = 0; i < repeats; i++)
        {
            init_dp_tables(&dp, n);
            barrier(&dp);
        }
        emit_affine("dp_init_call", round, repeats, writes * repeats, start);
        check_work_units("dp_init_call", WORK_DP_INIT_CALL, before_call, repeats);
        check_work_units("dp_init_write", WORK_DP_INIT_WRITE, before_volume,
                         (unsigned long long)writes * repeats);
    }
    n = 7;
    scans = n * (n + 1) * n;
    for (density = 0; density <= n; density++)
    {
        for (j = 0; j < n; j++)
            domains[j] = (1 << density) - 1;
        updates = n * (n + 1) * density;
        init_dp_tables(&dp, n);
        before_call = work_get(WORK_DP_SUFFIX_CANDIDATE_SCAN);
        before_volume = work_get(WORK_PROPAGATE_DP_UPDATE);
        start = clock_seconds();
        for (i = 0; i < repeats; i++)
        {
            fill_suff_dp(&dp, domains, n);
            barrier(&dp);
        }
        emit_affine("dp_suffix_candidate_scan", round, scans * repeats,
                    updates * repeats, start);
        check_work_units("dp_suffix_candidate_scan", WORK_DP_SUFFIX_CANDIDATE_SCAN,
                         before_call, (unsigned long long)scans * repeats);
        check_work_units("propagate_dp_update", WORK_PROPAGATE_DP_UPDATE,
                         before_volume, (unsigned long long)updates * repeats);
    }
}

static void bench_dp_scans(int repeats, int round)
{
    int i, k, m, scanned;
    int domains[9];
    t_dp_tables dp;
    t_prune_args args = {0};
    double start;
    unsigned long long before;

    prepare(7);
    node.domain.is_invalid = 0;
    for (i = 0; i < 7; i++)
    {
        /* The first cell is the tallest building; subsequent heights
         * stay below it, so clue 1 permits every remaining candidate.
         */
        domains[i] = (i == 0) ? 0x40 : 0x3f;
        node.domain.vals[i] = 0;
        node.domain.valid_val_bmps[i] = domains[i];
        node.domain.num_cell_vals[i] = (i == 0) ? 1 : 6;
        puzzle.constr_bounds.cur_c_pair.grid_indeces[i] = i;
    }
    /* Warm up the actual DP calculation outside the timed loop. Repeating
     * the same DP fill is stable; timing init_dp_tables here would attribute
     * DP initialization writes to the prefix/suffix scan counters.
     */
    init_dp_tables(&dp, 7);
    fill_pref_dp(&dp, domains, 7);
    scanned = 0;
    for (k = 0; k < 7; k++)
        for (m = 0; m <= 7; m++)
            if (dp.pref_max[k][m] != -1)
                scanned += 7;
    before = work_get(WORK_DP_PREFIX_CANDIDATE_SCAN);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        fill_pref_dp(&dp, domains, 7);
        barrier(&dp);
    }
    check_work_units("dp_prefix_candidate_scan",
                     WORK_DP_PREFIX_CANDIDATE_SCAN, before,
                     (unsigned long long)scanned * repeats);
    emit_individual("dp_prefix_candidate_scan", round,
                    scanned * repeats, start);

    init_dp_tables(&dp, 7);
    fill_suff_dp(&dp, domains, 7);
    before = work_get(WORK_DP_SUFFIX_CANDIDATE_SCAN);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        fill_suff_dp(&dp, domains, 7);
        barrier(&dp);
    }
    check_work_units("dp_suffix_candidate_scan",
                     WORK_DP_SUFFIX_CANDIDATE_SCAN, before,
                     7ULL * 8 * 7 * repeats);
    /* Suffix scan cost comes from the density-controlled affine experiment. */
    (void)start;

    /* Use complete, mutually consistent tables and valid domains. With
     * clue 1 and these clue-consistent domains, every value is feasible, so
     * prune_candidates must not modify the puzzle between repetitions.
     */
    init_dp_tables(&dp, 7);
    fill_pref_dp(&dp, domains, 7);
    fill_suff_dp(&dp, domains, 7);
    args.solver = &puzzle;
    args.state = &node;
    args.size = 7;
    args.target_clue = 1;
    args.dp = &dp;
    args.grid_indices = puzzle.constr_bounds.cur_c_pair.grid_indeces;
    before = work_get(WORK_DP_PRUNE_VALUE_SCAN);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        if (prune_candidates(&args) != 0 || node.domain.is_invalid)
        {
            fprintf(stderr, "DP microbenchmark changed its domain state\n");
            exit(3);
        }
        barrier(&node);
    }
    check_work_units("dp_prune_value_scan", WORK_DP_PRUNE_VALUE_SCAN,
                     before, 49ULL * repeats);
    emit_individual("dp_prune_value_scan", round, 49 * repeats, start);
}


/* Additional real solver operations that can become collinear under another
 * calibration seed. All paths check that their actual work units were seen
 * by the instrumented shadow executable, but the timing binary is native.
 * Counters with no meaningful active implementation in this workload remain
 * explicitly unbenchmarked rather than being given fabricated costs.
 */
static void bench_extra_counters(int repeats, int round)
{
    int i, j;
    double start;
    unsigned long long before;
    t_node_order *cache = &puzzle.order_stack.orders[0];
    t_lookahead_ctx *ctx = &puzzle.lookahead_stack[0];
    t_node_transition next;

    prepare(7);
    cache->items.count = 16;
    for (j = 0; j < 16; j++)
    {
        cache->items.entries[j].cell_idx = j;
        cache->items.entries[j].cell_val = 1;
        cache->items.meta[j].cached_br_score = 1.0;
        node.domain.vals[j] = 1;
    }
    node.lookahead_ctx = ctx;
    ctx->probe_pass = LOOKAHEAD_NONE;
    ctx->selectivity = SELECTIVITY_VALUE_SET;
    for (j = 0; j < 49; j++)
        ctx->cell_passes[j] = 0;
    before = work_get(WORK_LOOKAHEAD_SCAN);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        next.cell_idx = -1;
        next.cell_val = 1;
        if (get_next_lookahead(&puzzle, &next))
        {
            fprintf(stderr, "Lookahead scan unexpectedly selected a value\n");
            exit(3);
        }
        barrier(ctx);
    }
    check_work_units("lookahead_scan", WORK_LOOKAHEAD_SCAN, before,
                     16ULL * (unsigned long long)repeats);
    emit_individual("lookahead_scan", round, 16 * repeats, start);

    before = work_get(WORK_RESUME_SCAN);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        next.cell_idx = 48;
        next.cell_val = 1;
        get_next_lookahead(&puzzle, &next);
        barrier(ctx);
    }
    check_work_units("resume_scan", WORK_RESUME_SCAN, before,
                     16ULL * (unsigned long long)repeats);
    emit_individual("resume_scan", round, 16 * repeats, start);

    cache->state.lookahead_build_entropy = -1;
    before = work_get(WORK_RESCORE_SCAN);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        recalculate_cache_scores(&node, cache);
        barrier(cache);
    }
    check_work_units("rescore_scan", WORK_RESCORE_SCAN, before,
                     16ULL * (unsigned long long)repeats);
    emit_individual("rescore_scan", round, 16 * repeats, start);

    prepare(7);
    next.cell_idx = 0;
    next.cell_val = 1;
    before = work_get(WORK_BASE_SCORE);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        score_transition_full(&node, &next);
        barrier(&next);
    }
    check_work_units("base_score", WORK_BASE_SCORE, before,
                     (unsigned long long)repeats);
    emit_individual("base_score", round, repeats, start);

    puzzle.constr_max_entropy = 100;
    before = work_get(WORK_REL_ENTROPY_VALUE);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        sink += (unsigned long long)get_relative_constr_entropy(&node, 0, 7);
        barrier(&node);
    }
    check_work_units("rel_entropy_value", WORK_REL_ENTROPY_VALUE, before,
                     7ULL * (unsigned long long)repeats);
    emit_individual("rel_entropy_value", round, 7 * repeats, start);

    before = work_get(WORK_NODE_COPY);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        /* The same full-node copy performed by enter_search_child(). */
        puzzle.node_stack[1] = puzzle.node_stack[0];
        barrier(&puzzle.node_stack[1]);
        sink += (unsigned long long)puzzle.node_stack[1].size;
    }
    /* This copy is a real operation, but not the wrapper that increments
     * WORK_NODE_COPY; count the executed copies explicitly via loop size.
     */
    check_work_units("node_copy_is_not_instrumented_here",
                     WORK_NODE_COPY, before, 0);
    emit_individual("node_copy", round, repeats, start);

    before = work_get(WORK_SOLUTION_COPY);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        puzzle.sol_node_storage = node;
        barrier(&puzzle.sol_node_storage);
        sink += (unsigned long long)puzzle.sol_node_storage.size;
    }
    check_work_units("solution_copy_is_not_instrumented_here",
                     WORK_SOLUTION_COPY, before, 0);
    emit_individual("solution_copy", round, repeats, start);

    /* Actual score-blending operation, with its nontrivial branch active. */
    prepare(7);
    cache->items.count = 1;
    cache->state.lookahead_build_entropy = 100;
    cache->items.meta[0].cached_br_score = 1.0;
    cache->items.meta[0].entropy_pos = 30;
    cache->items.meta[0].entropy_neg = 70;
    node.domain.remaining_entropy = 100;
    puzzle.max_entropy = 1000;
    before = work_get(WORK_LOOKAHEAD_BLEND);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        sink += (unsigned long long)calculate_blended_score(&node, cache, 0);
        barrier(cache);
    }
    check_work_units("lookahead_blend", WORK_LOOKAHEAD_BLEND, before,
                     (unsigned long long)repeats);
    emit_individual("lookahead_blend", round, repeats, start);

    /* Provisional rollback is a rare but legitimate event counter. */
    before = work_get(WORK_PROVISIONAL_SOLUTION_ROLLBACK);
    start = clock_seconds();
    for (i = 0; i < repeats; i++)
    {
        puzzle.provisional_solution = 1;
        puzzle.solutions_found = 1;
        rollback_provisional_solution(&puzzle);
        barrier(&puzzle);
    }
    check_work_units("provisional_solution_rollback",
                     WORK_PROVISIONAL_SOLUTION_ROLLBACK, before,
                     (unsigned long long)repeats);
    emit_individual("provisional_solution_rollback", round, repeats, start);

    /* A successful domain invalidation with real bookkeeping, measured
     * inclusively. Reset a coherent state so each repetition is comparable.
     */
    prepare(7);
    for (i = 0; i < 49; i++)
    {
        puzzle.grid_constr_map[i][0] = i % 7;
        puzzle.grid_constr_map[i][1] = 7 + i / 7;
    }
    for (i = 0; i < 14; i++)
        for (j = 0; j < 7; j++)
            node.domain.constrs.num_val_positions[i][j] = 7;
    {
        t_node_state clean = node;
        before = work_get(WORK_DOMAIN_INVALIDATION);
        start = clock_seconds();
        for (i = 0; i < repeats; i++)
        {
            node = clean;
            set_value_invalid_internal(&node, 0, 1);
            barrier(&node);
            sink += (unsigned long long)node.domain.num_cell_vals[0];
        }
        check_work_units("domain_invalidation", WORK_DOMAIN_INVALIDATION,
                         before, (unsigned long long)repeats);
        emit_individual("domain_invalidation", round, repeats, start);
    }

    /* Genuine line scoring. This is an inclusive call-level benchmark:
     * sorting comparisons also occur, so interpret its estimate carefully.
     */
    prepare(7);
    {
        t_line_order *order = &puzzle.line_order_stack.orders[0];
        order->count = 14;
        for (i = 0; i < 14; i++)
        {
            order->entries[i].constr_idx = i;
            for (j = 0; j < 7; j++)
                node.domain.constrs.num_val_positions[i][j] = 7;
        }
        before = work_get(WORK_LINE_SCORE);
        start = clock_seconds();
        for (i = 0; i < repeats; i++)
        {
            sort_line_order(&node);
            barrier(order);
        }
        check_work_units("line_score", WORK_LINE_SCORE, before,
                         14ULL * (unsigned long long)repeats);
        emit_individual("line_score", round, 14 * repeats, start);
    }
    prepare(7);
}

int main(int argc, char **argv)
{
    int repeats, round;
    if (argc != 3 || sscanf(argv[1], "%d", &repeats) != 1 ||
        sscanf(argv[2], "%d", &round) != 1 || repeats < 1000 ||
        repeats > 4000000 || round < 0)
        return 2;
    prepare(7);
    benchmark_affine(repeats, round);
    bench_setup(repeats, round);
    bench_copies(repeats, round);
    bench_compact(repeats, round);
    bench_sort(repeats, round);
    bench_constraint_affine(repeats, round);
    bench_assignment(repeats, round);
    bench_constraint_subtasks(repeats, round);
    bench_cache_traversals(repeats, round);
    bench_prune_line_scan(repeats, round);
    bench_dp_affine(repeats, round);
    bench_dp_scans(repeats, round);
    bench_extra_counters(repeats, round);
    if (sink == 0xFFFFFFFFFFFFFFFFULL)
        fprintf(stderr, "sink=%llu\n", sink);
    return 0;
}
