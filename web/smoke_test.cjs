const makeSolver = require("./solver.js");

makeSolver().then((Module) => {
  const clues = "1 3 3 0 0 0 0 2 0 0 0 0 0 0 0 0";
  const result = Module.ccall("solve_web", "string",
    ["string", "string", "number"], [clues, "", 2]);
  const [count, nodes, size, grid] = result.split("|");
  if (count !== "2" || size !== "4" || grid.length !== 16) {
    throw new Error("Unexpected WebAssembly result: " + result);
  }
  console.log("WASM smoke test passed: " + count + " solutions, " + nodes + " nodes");
}).catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
