# Static website and assets

The site is published on GitHub Pages. All processing and random selection run
in the browser, with no server-side endpoints.

Production publishing runs when website files, published puzzle banks, or the
metadata exporter change, and when a stable GitHub release is published. Manual
publishing remains available. The workflow checks out the site and puzzle data
from `main`, resolves GitHub's latest published release (excluding drafts and
prereleases), and compiles and smoke-tests that release's C sources and WASM
wrapper in a separate checkout. It never falls back to unreleased solver code.
The release must contain `web/wasm_api.c` and `web/smoke_test.cjs`; v1.0.0 is the
first release with this browser support.

CI's WASM job still builds the code under test on `main` pushes and pull
requests. PR website previews also build the PR's solver so changes can be
reviewed before release.

- `/`: homepage, with links to `/demo/`, `/curated/`, and `/assets/`
- `/demo/`: WebAssembly solver demo; defaults to dark unless opened from the homepage
  with `?from=index&theme=light`. Direct `?theme=light` and
  `?theme=dark` links select the initial theme; a client-side toggle updates the
  query without reloading. The back-to-index link appears only for `from=index`.
- `/curated/`: difficulty distribution, percentiles and histograms
- `/assets/`: browsable asset directories and `/assets/index.json` endpoint catalog
- `/assets/solver/`: compiled solver, WASM and worker; a formatted usage guide
  appears *beneath* the directory listing (the parent `/assets/` listing has no
  extra description). The guide is maintained in `web/solver-description.html`.
- `/assets/puzzles/unique/v1/minimal/size_N.json`: unique puzzle banks
- `/assets/puzzles/curated/v1/metadata.json`: available size/difficulty counts
- `/assets/puzzles/curated/v1/statistics.json`: precomputed explorer statistics
- `/assets/puzzles/curated/v1/N/LEVEL.json`: published curated shards
- `/assets/puzzles/puzzles.js`: browser-side random and ID-based puzzle API

Import the API as an ES module from the deployed site:

```js
import { getRandomPuzzle, getPuzzleById, getMetadata } from
  "https://tonycongqianwang.github.io/SkyscraperSolver/assets/puzzles/puzzles.js";
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
