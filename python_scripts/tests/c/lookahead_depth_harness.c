#include <assert.h>
#include <string.h>
#include "puzzle_init.h"
#include "pruning_configs.h"
#include "prune_lookahead.h"
#include "solution_storage.h"

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

int main(void)
{
#ifdef CI_LOOKAHEAD_DEPTH
    const int expected[MAX_LOOKAHEAD_DEPTH][PRUNE_TIER_COUNT] = {{3, 2, 1}, {2, 0, 0}, {1, 0, 0}};
#else
    const int expected[MAX_LOOKAHEAD_DEPTH][PRUNE_TIER_COUNT] = {{1, 1, 1}, {1, 1, 1}, {1, 1, 1}};
#endif
    t_prune_routine_cfg config;
    int nesting, tier, depth;

    assert(init_puzzle(&puzzle, 4, 0));
    for (nesting = 0; nesting <= MAX_LOOKAHEAD_DEPTH + 1; ++nesting)
    {
        puzzle.cur_node->tree.lookahead_depth = nesting;
        for (tier = 0; tier < PRUNE_TIER_COUNT; ++tier)
        {
            init_prune_cfg(&config, tier, nesting, puzzle.size);
            depth = nesting < MAX_LOOKAHEAD_DEPTH ? expected[nesting][tier] : 0;
            assert(config.lookahead.max_depth == depth);
            assert(config.run_lookahead == (depth > 0));
            if (depth == 0)
                assert_skipped(&config.lookahead);
            /* Explicit zero configs must skip even outside the tier pipeline. */
            config.lookahead.max_depth = 0;
            assert_skipped(&config.lookahead);
        }
    }
    free_solution_storage(&puzzle);
    return 0;
}
