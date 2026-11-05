#include "puzzle_init.h"
#include "prune_check_constr.h"
#include "node_selection_score.h"
#include "node_selection_transition.h"
#include "solution_storage.h"
#include <assert.h>
#include <limits.h>
#include <math.h>
#include <stddef.h>

static t_puzzle g_puzzle;

static void test_signed_dp_sentinels(void)
{
    t_dp_tables dp;

    init_dp_tables(&dp, 1);
    assert(dp.pref_max[1][1] == -1);
    assert(dp.suff_max[0][1] == -1);
    assert(dp.pref_min[1][1] == 100);
    assert(dp.suff_min[0][1] == 100);
}

static void test_one_cell_scores(void)
{
    t_node_transition tr;
    t_node_order *cache;

    assert(init_puzzle(&g_puzzle, 1, 1));
    init_node_transition(&tr);
    tr.cell_idx = 0;
    tr.cell_val = 1;
    score_transition_strat(g_puzzle.cur_node, &tr);
    assert(isfinite(tr.score));
    cache = g_puzzle.cur_node->order_cache;
    cache->meta[0].entropy_pos = -1;
    cache->meta[0].entropy_neg = -1;
    cache->meta[0].cached_br_score = tr.score;
    cache->lookahead_build_entropy = 0;
    assert(isfinite(calculate_blended_score(g_puzzle.cur_node, cache, 0)));
    free_solution_storage(&g_puzzle);
}

static void test_storage_overflow(void)
{
    assert(!init_solution_storage(&g_puzzle, ULLONG_MAX));
    assert(g_puzzle.solutions == NULL);
    assert(init_solution_storage(&g_puzzle, 0));
    assert(g_puzzle.solutions == &g_puzzle.sol_node_storage);
}

int main(void)
{
    test_signed_dp_sentinels();
    test_one_cell_scores();
    test_storage_overflow();
    return (0);
}
