importScripts("./solver.js");
let modulePromise = null;
self.onmessage = async ({data}) => {
  try {
    if (!modulePromise) modulePromise = createSkyscraperSolver();
    const Module = await modulePromise;
    const response = Module.ccall("solve_web", "string",
      ["string", "string", "number"],
      [data.clues, data.grid || "", data.limit]);
    self.postMessage({ response });
  } catch (error) {
    self.postMessage({ error: String(error) });
  }
};
