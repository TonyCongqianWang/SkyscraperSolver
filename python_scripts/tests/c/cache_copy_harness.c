#include <assert.h>
#include <string.h>
#include "node_selection_cache.h"

static t_node_order source;
static t_node_order target;
static t_node_order before;

static void check_copy(int count)
{
    int i;
    memset(&source, 0x3b, sizeof(source));
    memset(&target, 0xa5, sizeof(target));
    source.items.count = count;
    source.state.lookahead_build_entropy = 1234;
    source.state.scores_dirty = 1;
    source.state.order_dirty = 1;
    source.state.order_criterion = SELECT_MIN;
    source.state.build_depth = 7;
    for (i = 0; i < ORDER_REFRESH_COUNT; i++)
        source.state.refresh_entropy[i] = 100 + i;
    for (i = 0; i < count; i++)
    {
        source.items.entries[i].cell_idx = i / 9;
        source.items.entries[i].cell_val = i % 9 + 1;
        source.items.entries[i].score = i * .5;
        source.items.meta[i].cached_br_score = i * .25;
        source.items.meta[i].entropy_pos = i + 1;
        source.items.meta[i].entropy_neg = i + 2;
    }
    before = target;
    copy_order_items(&target.items, &source.items);
    assert(memcmp(&target.state, &before.state, sizeof(target.state)) == 0);
    copy_node_order(&target, &source);
    assert(target.items.count == count);
    assert(memcmp(&target.state, &source.state, sizeof(source.state)) == 0);
    assert(memcmp(target.items.entries, source.items.entries,
                  count * sizeof(source.items.entries[0])) == 0);
    assert(memcmp(target.items.meta, source.items.meta,
                  count * sizeof(source.items.meta[0])) == 0);
    /* Inactive capacity must not be copied, cleared, or examined as entries. */
    assert(memcmp(target.items.entries + count, before.items.entries + count,
                  (MAX_TRANSITIONS - count) * sizeof(source.items.entries[0])) == 0);
    assert(memcmp(target.items.meta + count, before.items.meta + count,
                  (MAX_TRANSITIONS - count) * sizeof(source.items.meta[0])) == 0);
    assert(source.items.count == count && source.state.order_dirty == 1);
}

int main(void)
{
    check_copy(0);
    check_copy(1);
    check_copy(17);
    check_copy(128);
    check_copy(MAX_TRANSITIONS);
    return 0;
}
