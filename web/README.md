# Static website and assets

The site is published on GitHub Pages. All processing and random selection run
in the browser, with no server-side endpoints.

- `/`: homepage, with links to `/demo/`, `/curated/`, and `/assets/`
- `/demo/`: WebAssembly solver demo
- `/curated/`: difficulty distribution, percentiles and histograms
- `/assets/`: browsable asset directories and `/assets/index.json` endpoint catalog
- `/assets/solver/`: compiled solver, WASM and worker
- `/assets/puzzles/unique/v1/minimal/size_N.json`: unique puzzle banks
- `/assets/puzzles/curated/v1/metadata.json`: available size/difficulty counts
- `/assets/puzzles/curated/v1/statistics.json`: precomputed explorer statistics
- `/assets/puzzles/curated/v1/N/LEVEL.json`: published curated shards
- `/assets/puzzles/random.js`: browser-side random and ID-based puzzle API

Import the API as an ES module from the deployed site:

```js
import { getRandomPuzzle, getPuzzleById, getMetadata } from
  "https://tonycongqianwang.github.io/SkyscraperSolver/assets/puzzles/random.js";
const puzzle = await getRandomPuzzle({ size: 7, difficulty: "extreme_plus" });
const samePuzzle = await getPuzzleById(puzzle.puzzle_id);
```

Both filters are optional. Selection is uniform across matching records,
with replacement. The module downloads only the selected shard, caches
in-flight and completed requests, and evicts failed requests for retry.
Each puzzle includes source metadata, size, difficulty, and a version-tagged `puzzle_id` (`v1:<size>:<difficulty>:<original-id>`), while preserving the original `id`. `getPuzzleById` parses that ID and loads only the corresponding shard; unknown IDs reject with `RangeError`. The API is a
JavaScript module, not a dynamic HTTP JSON endpoint.

Generate the static site from hydrated LFS puzzle banks with:

```sh
python3 web/build_site.py --output public
```

Compile Emscripten output into `public/assets/solver/solver.js` first.
`web/endpoint_registry.py` is the shared route registry that creates
intermediate indexes and the machine-readable catalog. Generated pages and
API paths are relative, so GitHub Pages project-site prefixes work.
