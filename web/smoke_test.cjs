const makeSolver = require("./solver.js");

makeSolver().then((Module) => {
  const clues = "1 3 3 0 0 0 0 2 0 0 0 0 0 0 0 0";
  const result = Module.ccall("solve_web", "string",
    ["string", "string", "number"], [clues, "", 2]);
  const [count, nodes, size, grid] = result.split("|");
  if (count !== "2" || size !== "4" || grid.length !== 16) {
    throw new Error("Unexpected WebAssembly result: " + result);
  }
  const solvedGrid = "4 2 1 3 3 1 2 4 2 3 4 1 1 4 3 2";
  const given = Module.ccall("solve_web", "string",
    ["string", "string", "number"], [clues, solvedGrid, 2]);
  if (!given.startsWith("1|")) {
    throw new Error("Expected a unique fully given grid: " + given);
  }
  console.log("WASM smoke test passed: " + count + " solutions, " + nodes + " nodes");
}).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
