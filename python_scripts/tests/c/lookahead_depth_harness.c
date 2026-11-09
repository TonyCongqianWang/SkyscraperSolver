#include <assert.h>
#include <string.h>
#include "puzzle_init.h"
#include "pruning_configs.h"
#include "prune_lookahead.h"
#include "solution_storage.h"
#include "lookahead_dive.h"

static t_solver_state puzzle;

static void assert_skipped(t_lookahead_config *config)
{
    t_node_state before = *puzzle.cur_node;
    t_node_order cache = *puzzle.cur_node->order_cache;
    t_node_count visited = puzzle.nodes_visited;

    run_lookahead(&puzzle, puzzle.cur_node, config);
    assert(puzzle.nodes_visited == visited);
    assert(memcmp(&before, puzzle.cur_node, sizeof(before)) == 0);
    assert(memcmp(&cache, puzzle.cur_node->order_cache, sizeof(cache)) == 0);
}

static t_probe_depth wanted;
static int positive_calls, negative_calls;

t_probe_result __real_probe_assumption(t_solver_state *, t_node_transition,
                                      int, t_check_mode);
t_probe_result __real_probe_exclusion(t_solver_state *, t_node_transition,
                                     int, t_check_mode);

t_probe_result __wrap_probe_assumption(t_solver_state *solver,
    t_node_transition next, int depth, t_check_mode mode)
{
    assert(wanted.positive > 0 && depth == wanted.positive);
    ++positive_calls;
    return __real_probe_assumption(solver, next, depth, mode);
}

t_probe_result __wrap_probe_exclusion(t_solver_state *solver,
    t_node_transition next, int depth, t_check_mode mode)
{
    assert(wanted.negative > 0 && depth == wanted.negative);
    ++negative_calls;
    return __real_probe_exclusion(solver, next, depth, mode);
}

static void check_sides(int positive, int negative)
{
    t_lookahead_config config;
    memset(&puzzle, 0, sizeof(puzzle));
    assert(init_puzzle(&puzzle, 4, 0));
    /* Keep nested pruning from starting more probes during this trace. */
    puzzle.cur_node->tree.lookahead_depth = MAX_LOOKAHEAD_DEPTH - 1;
    memset(&config, 0, sizeof(config));
    config.selectivity = SELECTIVITY_NONE;
    config.passes = LOOKAHEAD_BOTH;
    config.check_mode = g_check_constr;
    config.depth.positive = positive;
    config.depth.negative = negative;
    wanted = config.depth;
    positive_calls = 0;
    negative_calls = 0;
    run_lookahead(&puzzle, puzzle.cur_node, &config);
    assert((positive_calls > 0) == (positive > 0));
    assert((negative_calls > 0) == (negative > 0));
    assert(!puzzle.cur_node->domain.is_invalid);
    free_solution_storage(&puzzle);
}

int main(void)
{
#ifdef CI_LOOKAHEAD_DEPTH
    const t_probe_depth expected[MAX_LOOKAHEAD_DEPTH][PRUNE_TIER_COUNT] = {
        {{3, 3}, {2, 2}, {1, 1}}, {{2, 2}, {0, 0}, {0, 0}},
        {{1, 1}, {0, 0}, {0, 0}}};
#elif defined(MARKING_LOOKAHEAD_DEPTH)
    const t_probe_depth expected[MAX_LOOKAHEAD_DEPTH][PRUNE_TIER_COUNT] = {
        {{1, 1}, {1, 1}, {3, 1}}, {{1, 0}, {0, 0}, {0, 0}},
        {{0, 0}, {0, 0}, {0, 0}}};
#else
    const t_probe_depth expected[MAX_LOOKAHEAD_DEPTH][PRUNE_TIER_COUNT] = {
        {{1, 1}, {1, 1}, {1, 1}}, {{1, 1}, {1, 1}, {1, 1}},
        {{1, 1}, {1, 1}, {1, 1}}};
#endif
    t_prune_routine_cfg config;
    int nesting, tier, positive, negative;

    assert(init_puzzle(&puzzle, 4, 0));
    for (nesting = 0; nesting <= MAX_LOOKAHEAD_DEPTH + 1; ++nesting)
    {
        puzzle.cur_node->tree.lookahead_depth = nesting;
        for (tier = 0; tier < PRUNE_TIER_COUNT; ++tier)
        {
            init_prune_cfg(&config, tier, nesting);
            positive = nesting < MAX_LOOKAHEAD_DEPTH ? expected[nesting][tier].positive : 0;
            negative = nesting < MAX_LOOKAHEAD_DEPTH ? expected[nesting][tier].negative : 0;
            assert(config.lookahead.depth.positive == positive);
            assert(config.lookahead.depth.negative == negative);
            assert(config.run_lookahead == (positive > 0 || negative > 0));
            if (positive == 0 && negative == 0)
                assert_skipped(&config.lookahead);
            config.lookahead.depth.positive = 0;
            config.lookahead.depth.negative = 0;
            assert_skipped(&config.lookahead);
            /* A nonzero depth cannot enable a direction excluded by passes. */
            config.lookahead.depth.negative = 1;
            config.lookahead.passes = LOOKAHEAD_POS;
            assert_skipped(&config.lookahead);
            config.lookahead.depth.positive = 1;
            config.lookahead.depth.negative = 0;
            config.lookahead.passes = LOOKAHEAD_NEG;
            assert_skipped(&config.lookahead);
        }
    }
    free_solution_storage(&puzzle);
    check_sides(1, 0);
    check_sides(0, 1);
    check_sides(2, 1);
    return 0;
}
