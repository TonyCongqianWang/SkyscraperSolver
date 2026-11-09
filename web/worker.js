const solverPath = new URL(self.location.href).searchParams.get("solver") || "solver.js";
if (!["solver.js", "release/solver.js", "prerelease/solver.js"].includes(solverPath)) {
  throw new Error("Unknown solver version");
}
const solverUrl = new URL(solverPath, self.location.href);
importScripts(solverUrl.href);
let modulePromise = null;
self.onmessage = async ({data}) => {
  try {
    if (!modulePromise) modulePromise = createSkyscraperSolver({
      locateFile: filename => new URL(filename, solverUrl).href,
    });
    const Module = await modulePromise;
    const response = Module.ccall("solve_web", "string",
      ["string", "string", "number"],
      [data.clues, data.grid || "", data.limit]);
    self.postMessage({ response });
  } catch (error) {
    self.postMessage({ error: String(error) });
  }
};
