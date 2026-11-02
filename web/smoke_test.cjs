const makeSolver = require("./solver.js");

makeSolver().then((Module) => {
  const clues = "1 3 3 0 0 0 0 2 0 0 0 0 0 0 0 0";
  const result = Module.ccall("solve_web", "string",
    ["string", "string", "number"], [clues, "", 2]);
  const [count, nodes, size, grid] = result.split("|");
  if (count !== "2" || size !== "4" || grid.length !== 16) {
    throw new Error("Unexpected WebAssembly result: " + result);
  }
  // Use the actual solution returned above, rather than an unrelated Latin square.
  const solvedGrid = [...grid].join(" ");
  const given = Module.ccall("solve_web", "string",
    ["string", "string", "number"], [clues, solvedGrid, 2]);
  if (!given.startsWith("1|")) {
    throw new Error("Expected a unique fully given grid: " + given);
  }
  // Repeat with a partial initial grid, which may cause propagation to
  // fill other givens before their turn in the initial update batch.
  for (const filled of [1, 4, 8, 12, 15]) {
    const partialGrid = [...grid].map((value, index) =>
      index < filled ? value : "0").join(" ");
    const partial = Module.ccall("solve_web", "string",
      ["string", "string", "number"], [clues, partialGrid, 2]);
    const [partialCount] = partial.split("|");
    if (Number(partialCount) < 1 || Number(partialCount) > 2) {
      throw new Error("Partial grid (first " + filled +
        " givens) unexpectedly has no solution: " + partial);
    }
  }
  console.log("WASM smoke test passed: " + count + " solutions, " + nodes + " nodes");
}).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
