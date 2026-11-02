# Curated puzzle browser API (v1)

GitHub Pages serves a **static ES module**, not a dynamic HTTP random endpoint.
The module selects a random entry in the browser and caches successful downloads.

```js
import { getMetadata, getRandomPuzzle } from
  "https://tonycongqianwang.github.io/SkyscraperSolver/puzzle-bank/curated/v1/api.js";

const metadata = await getMetadata();
const count = metadata.sizes["5"].medium;
if (count > 0) {
  const puzzle = await getRandomPuzzle({ size: 5, difficulty: "medium" });
  // puzzle.clues: top, bottom, left, right (flat, 4*size)
  // puzzle.givens and puzzle.canonical_solution: flat row-major (size*size)
}
```

The `metadata.json` endpoint contains `schema_version`, `curated_version`,
and `sizes[size][difficulty]` counts. Zero means the combination is unavailable.
Supported sizes: 4–9. Difficulty keys: `very_easy`, `easy`, `medium`,
`hard`, `very_hard`, `extreme`, `impossible`.

`getRandomPuzzle` rejects on network failures, unavailable combinations, or
invalid data. Consumers should catch the error, offer **Retry**, and optionally
generate a local fallback. A rejected fetch is evicted from the module cache so
retry actually refetches; successful responses are cached for the page lifetime.
Random selection is with replacement; uniqueness between calls is not promised.
Each record retains its curated ID and other source fields and adds `size`
and `difficulty`.

The Pages publishing workflow generates `metadata.json` from hydrated curated
size files and stages `api.js`. Run the metadata generator locally with:

```sh
python3 python_scripts/puzzle_bank/export_api_metadata.py
```

The size collections are downloaded whole on first use. Future sharding may
reduce initial bandwidth without changing the public JavaScript API.
