# Browser solver

Build locally with [Emscripten](https://emscripten.org/):

```sh
emcc -O3 -flto src/*.c web/wasm_api.c \
  -s MODULARIZE=1 -s EXPORT_NAME=createSkyscraperSolver \
  -s EXPORTED_FUNCTIONS='["_solve_web"]' \
  -s EXPORTED_RUNTIME_METHODS='["ccall"]' \
  -s ALLOW_MEMORY_GROWTH=1 -s INITIAL_MEMORY=67108864 \
  -o web/solver.js
```

The page communicates with a Web Worker to keep the main UI responsive. The C interface `solve_web(const char *clues, const char *grid, int max_solutions)` returns a transient string `count|nodes|size|row-major-first-solution` or `ERR:...`. Clues and optional grid follow the native CLI input format. Web page always uses a solution cap of two.

GitHub Actions publishes the compiled JS and WASM together with the puzzle bank to Pages.
