const assert = require("node:assert/strict");
const { test } = require("node:test");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map(match => match[1]);
assert.equal(scripts.length, 2, "theme initializer and solver script");

function openDemo(address, manifest = { default: "release", versions: [
  { id: "release", tag: "v1.0.0", path: "release/solver.js", prerelease: false },
  { id: "prerelease", tag: "v1.1.0-rc.1", path: "prerelease/solver.js", prerelease: true },
] }, fetchOk = true) {
  const elements = new Map();
  const document = {
    documentElement: { dataset: {} },
    createElement() { return { value: "", textContent: "" }; },
    getElementById(id) {
      if (!elements.has(id)) {
        elements.set(id, {
          hidden: false, textContent: "", attributes: {}, disabled: true,
          value: id === "clues" ? "1 3 3 0 0 0 0 2 0 0 0 0 0 0 0 0" : "",
          replaceChildren(...children) { this.children = children; },
          setAttribute(name, value) { this.attributes[name] = value; }
        });
      }
      return elements.get(id);
    }
  };
  const changes = [];
  const window = {
    location: new URL(address),
    history: {
      replaceState(_state, _title, url) {
        changes.push(String(url));
        window.location = new URL(url);
      }
    }
  };
  const workers = [];
  class Worker {
    constructor(url) { this.url = url; workers.push(this); }
    terminate() { this.terminated = true; }
    postMessage(data) { this.data = data; }
  }
  const context = vm.createContext({ document, window, URL, URLSearchParams, Worker,
    setTimeout, clearTimeout,
    fetch: async () => ({ ok: fetchOk, json: async () => manifest }),
  });
  for (const script of scripts) vm.runInContext(script, context);
  return { document, window, changes, elements, workers,
    ready: vm.runInContext("versionsReady", context) };
}

test("direct visits default to existing dark theme, with no back link", () => {
  const demo = openDemo("https://example.com/SkyscraperSolver/demo/");
  assert.equal(demo.document.documentElement.dataset.theme, "dark");
  assert.equal(demo.elements.get("back-home").hidden, true);
  assert.equal(demo.elements.get("theme-toggle").textContent, "Light theme");
  assert.equal(demo.changes.length, 0);
});

test("homepage origin defaults to light and reveals a relative back link", () => {
  const demo = openDemo("https://example.com/SkyscraperSolver/demo/?from=index");
  assert.equal(demo.document.documentElement.dataset.theme, "light");
  assert.equal(demo.elements.get("back-home").hidden, false);
  assert.match(html, /id="back-home" href="\.\.\/"/);
  assert.equal(demo.elements.get("theme-toggle").textContent, "Dark theme");
});

test("explicit theme query overrides source and invalid values use default", () => {
  const light = openDemo("https://example.com/SkyscraperSolver/demo/?theme=light");
  assert.equal(light.document.documentElement.dataset.theme, "light");
  assert.equal(light.elements.get("back-home").hidden, true);
  const dark = openDemo("https://example.com/SkyscraperSolver/demo/?from=index&theme=dark");
  assert.equal(dark.document.documentElement.dataset.theme, "dark");
  assert.equal(dark.elements.get("back-home").hidden, false);
  const invalid = openDemo("https://example.com/SkyscraperSolver/demo/?theme=invalid");
  assert.equal(invalid.document.documentElement.dataset.theme, "dark");
});

test("toggle changes theme without navigation and updates shareable query", () => {
  const demo = openDemo("https://example.com/SkyscraperSolver/demo/?from=index&theme=light&debug=1");
  demo.elements.get("theme-toggle").onclick();
  assert.equal(demo.document.documentElement.dataset.theme, "dark");
  assert.equal(demo.elements.get("theme-toggle").textContent, "Light theme");
  assert.equal(demo.elements.get("theme-toggle").attributes["aria-label"],
    "Switch to light theme");
  assert.equal(demo.window.location.searchParams.get("theme"), "dark");
  assert.equal(demo.window.location.searchParams.get("from"), "index");
  assert.equal(demo.window.location.searchParams.get("debug"), "1");
  assert.equal(demo.changes.length, 1);
  demo.elements.get("theme-toggle").onclick();
  assert.equal(demo.document.documentElement.dataset.theme, "light");
  assert.equal(demo.window.location.searchParams.get("theme"), "light");
  assert.equal(demo.changes.length, 2);
});

test("homepage link opts into light mode", () => {
  const home = fs.readFileSync(path.join(__dirname, "home.html"), "utf8");
  assert.match(home, /href="\.\/demo\/\?from=index&amp;theme=light"/);
  assert.match(html, /:root\[data-theme="light"\]/);
});

test("version selector defaults to release and switching cancels pending work", async () => {
  const demo = openDemo("https://example.com/SkyscraperSolver/demo/");
  await demo.ready;
  const select = demo.elements.get("solver-version");
  assert.equal(select.value, "release/solver.js");
  assert.deepEqual(Array.from(select.children, option => option.textContent),
    ["v1.0.0 (release)", "v1.1.0-rc.1 (prerelease)"]);
  assert.equal(select.disabled, false);
  const solve = demo.elements.get("solve");
  solve.onclick();
  assert.match(demo.workers[0].url, /solver=release%2Fsolver.js$/);
  assert.equal(solve.disabled, true);
  select.value = "prerelease/solver.js";
  select.onchange();
  assert.equal(demo.workers[0].terminated, true);
  assert.equal(solve.disabled, false);
  solve.onclick();
  assert.match(demo.workers[1].url, /solver=prerelease%2Fsolver.js$/);
  // Queued messages from a terminated worker must not overwrite the new solve.
  demo.workers[0].onmessage({ data: { error: "stale result" } });
  assert.equal(solve.disabled, true);
  assert.equal(demo.workers[1].terminated, undefined);
  demo.workers[1].onmessage({ data: { response: "1|42|4|1234341221434321" } });
  assert.equal(solve.disabled, false);
  assert.match(demo.elements.get("status").textContent, /Unique solution.*42/);
});

test("a prerelease-only manifest has no release option and is ready to solve", async () => {
  const demo = openDemo("https://example.com/demo/", { default: "prerelease", versions: [
    { id: "prerelease", tag: "v0.9.1", path: "prerelease/solver.js", prerelease: true },
  ] });
  await demo.ready;
  const select = demo.elements.get("solver-version");
  assert.equal(select.children.length, 1);
  assert.equal(select.value, "prerelease/solver.js");
  assert.equal(demo.elements.get("solve").disabled, false);
});

test("version loading failures leave solving disabled with a visible error", async () => {
  const demo = openDemo("https://example.com/demo/", null, false);
  await demo.ready;
  assert.equal(demo.elements.get("solve").disabled, true);
  assert.equal(demo.elements.get("solver-version").children.length, 0);
  assert.match(demo.elements.get("status").textContent, /Could not load solver versions/);
});
