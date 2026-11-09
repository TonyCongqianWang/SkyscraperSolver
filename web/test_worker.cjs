const assert = require("node:assert/strict");
const { test } = require("node:test");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");
const source = fs.readFileSync(path.join(__dirname, "worker.js"), "utf8");

for (const solver of ["solver.js", "release/solver.js", "prerelease/solver.js"]) {
  test(`worker loads ${solver} and its matching WASM under a project prefix`, async () => {
    let imported, wasm, calls = 0;
    const responses = [];
    const base = "https://example.com/SkyscraperSolver/assets/solver/";
    const self = {
      location: { href: base + "worker.js?solver=" + encodeURIComponent(solver) },
      postMessage: message => responses.push(message),
    };
    const context = vm.createContext({
      self, URL, importScripts: url => { imported = url; },
      createSkyscraperSolver: options => {
        calls++;
        wasm = options.locateFile("solver.wasm");
        return Promise.resolve({ ccall: () => "1|42|4|1234341221434321" });
      },
    });
    vm.runInContext(source, context);
    await self.onmessage({ data: { clues: "0", limit: 2 } });
    await self.onmessage({ data: { clues: "0", limit: 2 } });
    assert.equal(imported, base + solver);
    assert.equal(wasm, base + solver.replace(/\.js$/, ".wasm"));
    assert.equal(calls, 1);
    assert.equal(responses.length, 2);
    assert.match(responses[0].response, /^1\|42\|4\|/);
  });
}

test("worker rejects unexpected solver locations", () => {
  const context = vm.createContext({ URL, self: {
    location: { href: "https://example.com/assets/solver/worker.js?solver=https://other.example/solver.js" },
  } });
  assert.throws(() => vm.runInContext(source, context), /Unknown solver version/);
});
