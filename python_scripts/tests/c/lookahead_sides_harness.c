#include <assert.h>
#include <string.h>
#include "puzzle_init.h"
#include "prune_lookahead.h"
#include "grid_interface.h"
#include "solution_storage.h"

static t_puzzle puzzle;

static void check_side(t_lookahead_side side, t_selectivity_level selectivity)
{
    t_lookahead_config config;
    t_node_order *cache;
    int i;

    memset(&puzzle, 0, sizeof(puzzle));
    init_puzzle(&puzzle, 4, 1);
    memset(&config, 0, sizeof(config));
    config.selectivity = selectivity;
    config.max_depth = 1;
    config.lookahead_side = side;
    config.check_mode = g_check_constr;
    run_lookahead_loop(&puzzle, puzzle.cur_node, &config);
    assert(!puzzle.cur_node->is_invalid);
    assert(puzzle.cur_node->lookahead_ctx == NULL);
    cache = puzzle.cur_node->order_cache;
    assert(cache->count == 64);
    for (i = 0; i < cache->count; i++)
    {
        if (side != LOOKAHEAD_SIDE_NEG)
            assert(cache->meta[i].entropy_pos >= 0);
        else
            assert(cache->meta[i].entropy_pos == -1);
        if (side != LOOKAHEAD_SIDE_POS)
            assert(cache->meta[i].entropy_neg >= 0);
        else
            assert(cache->meta[i].entropy_neg == -1);
    }
    /* Each separate invocation must also start a fresh traversal. */
    for (i = 0; i < cache->count; i++)
    {
        cache->meta[i].entropy_pos = -1;
        cache->meta[i].entropy_neg = -1;
    }
    run_lookahead_loop(&puzzle, puzzle.cur_node, &config);
    cache = puzzle.cur_node->order_cache;
    for (i = 0; i < cache->count; i++)
    {
        if (side != LOOKAHEAD_SIDE_NEG)
            assert(cache->meta[i].entropy_pos >= 0);
        if (side != LOOKAHEAD_SIDE_POS)
            assert(cache->meta[i].entropy_neg >= 0);
    }
    free_solution_storage(&puzzle);
}

int main(void)
{
    t_lookahead_side sides[] = {
        LOOKAHEAD_SIDE_POS, LOOKAHEAD_SIDE_NEG, LOOKAHEAD_SIDE_BOTH};
    t_selectivity_level levels[] = {
        SELECTIVITY_VALUE_SET, SELECTIVITY_ANY_CHANGE, SELECTIVITY_NONE};
    int i;
    int j;

    for (i = 0; i < 3; i++)
        for (j = 0; j < 3; j++)
            check_side(sides[i], levels[j]);
    return (0);
}
