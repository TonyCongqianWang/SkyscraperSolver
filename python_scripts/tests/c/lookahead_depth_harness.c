#include <assert.h>
#include <string.h>
#include "puzzle_init.h"
#include "pruning_configs.h"
#include "prune_lookahead.h"
#include "solution_storage.h"
#include "lookahead_dive.h"
#include "prune_strat_root.h"
#include "params_double.h"

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
static int checking_extra;

t_probe_result __real_probe_assumption(t_solver_state *, t_node_transition,
                                      int, t_check_mode);
t_probe_result __real_probe_exclusion(t_solver_state *, t_node_transition,
                                     int, t_check_mode);

t_probe_result __wrap_probe_assumption(t_solver_state *solver,
    t_node_transition next, int depth, t_check_mode mode)
{
    if (checking_extra)
        assert(depth == (solver->cur_node->tree.lookahead_depth == 0 ? 3 : 1));
    else
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

static void check_tier_schedule(void)
{
    t_node_state *node;
    t_prune_routine_cfg config;
    int i, extra;
    memset(&puzzle, 0, sizeof(puzzle));
    assert(init_puzzle(&puzzle, 4, 0));
    node = puzzle.cur_node;
    node->domain.remaining_entropy = 1000;
    for (i = 0; i < PRUNE_TIER_COUNT; ++i) node->last_entropy[i] = 1000;
    assert(get_prune_tier_selectivity(PRUNE_EXTRA) == SELECTIVITY_NONE);
#ifdef MARKING_LOOKAHEAD_DEPTH
    extra = PRUNE_EXTRA;
#else
    extra = -1;
#endif
    node->last_entropy[PRUNE_EXTRA] = 1060;
    assert(select_prune_tier(node, 10.0, 2.0, 3.0) == -1);
    node->last_entropy[PRUNE_EXTRA] = 1061;
    assert(select_prune_tier(node, 10.0, 2.0, 3.0) == extra);
    /* The extra threshold follows the supplied heavy multiplier. */
    assert(select_prune_tier(node, 10.0, 2.0, 4.0) == -1);
    node->last_entropy[PRUNE_LIGHT] = 1011;
    assert(select_prune_tier(node, 10.0, 2.0, 3.0) == PRUNE_LIGHT);
    node->last_entropy[PRUNE_LIGHT] = 1000;
    node->last_entropy[PRUNE_MEDIUM] = 1021;
    assert(select_prune_tier(node, 10.0, 2.0, 3.0) == PRUNE_MEDIUM);
    node->last_entropy[PRUNE_MEDIUM] = 1000;
    node->last_entropy[PRUNE_HEAVY] = 1031;
    assert(select_prune_tier(node, 10.0, 2.0, 3.0) == PRUNE_HEAVY);
    /* Heavy resets lower clocks while preserving extra's accumulated delta. */
    init_prune_cfg(&config, PRUNE_HEAVY, 0);
    config.run_lookahead = 0;
    run_pruning_routine(&puzzle, &config, PRUNE_HEAVY);
    assert(node->last_entropy[PRUNE_EXTRA] == 1061);
    assert(select_prune_tier(node, 10.0, 2.0, 3.0) == extra);
    node->tree.lookahead_depth = 1;
    assert(select_prune_tier(node, 10.0, 2.0, 3.0) == -1);
    node->tree.lookahead_depth = 0;
    init_prune_cfg(&config, PRUNE_EXTRA, 0);
    config.run_lookahead = 0;
    run_pruning_routine(&puzzle, &config, PRUNE_EXTRA);
    for (i = 0; i < PRUNE_TIER_COUNT; ++i) assert(node->last_entropy[i] == 1000);
    assert(select_prune_tier(node, 10.0, 2.0, 3.0) == -1);
    free_solution_storage(&puzzle);
}

static void check_extra_dispatch(void)
{
#ifdef MARKING_LOOKAHEAD_DEPTH
    int entropy, tier;
    double saved_scale = g_root_period_coef_scale;
    double saved_unset = g_root_period_coef_unset;
    memset(&puzzle, 0, sizeof(puzzle));
    assert(init_puzzle(&puzzle, 4, 0));
    set_cell_invalid(&puzzle, 0, 4, g_check_constr);
    entropy = puzzle.cur_node->domain.remaining_entropy;
    /* Use a controlled period and real domain reduction to make extra due. */
    g_root_period_coef_scale = 0;
    g_root_period_coef_unset = 0;
    for (tier = PRUNE_LIGHT; tier <= PRUNE_HEAVY; ++tier)
        puzzle.cur_node->last_entropy[tier] = entropy;
    positive_calls = 0;
    negative_calls = 0;
    wanted.negative = 0;
    checking_extra = 1;
    prune_strat_root(&puzzle);
    checking_extra = 0;
    g_root_period_coef_scale = saved_scale;
    g_root_period_coef_unset = saved_unset;
    assert(positive_calls > 0 && negative_calls == 0);
    assert(!puzzle.cur_node->domain.is_invalid);
    assert(puzzle.cur_node->lookahead_ctx == NULL);
    assert(puzzle.cur_node->last_entropy[PRUNE_EXTRA] == entropy);
    free_solution_storage(&puzzle);
#endif
}

int main(void)
{
#ifdef CI_LOOKAHEAD_DEPTH
    const t_probe_depth expected[MAX_LOOKAHEAD_DEPTH][PRUNE_TIER_COUNT] = {
        {{3, 3}, {2, 2}, {1, 1}, {0, 0}}, {{2, 2}, {0, 0}, {0, 0}, {0, 0}},
        {{1, 1}, {0, 0}, {0, 0}, {0, 0}}};
#elif defined(MARKING_LOOKAHEAD_DEPTH)
    const t_probe_depth expected[MAX_LOOKAHEAD_DEPTH][PRUNE_TIER_COUNT] = {
        {{1, 1}, {1, 1}, {1, 1}, {3, 0}}, {{1, 0}, {0, 0}, {0, 0}, {0, 0}},
        {{0, 0}, {0, 0}, {0, 0}, {0, 0}}};
#else
    const t_probe_depth expected[MAX_LOOKAHEAD_DEPTH][PRUNE_TIER_COUNT] = {
        {{1, 1}, {1, 1}, {1, 1}, {0, 0}}, {{1, 1}, {1, 1}, {1, 1}, {0, 0}},
        {{1, 1}, {1, 1}, {1, 1}, {0, 0}}};
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
    check_tier_schedule();
    check_extra_dispatch();
    return 0;
}
