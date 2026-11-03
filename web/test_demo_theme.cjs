const assert = require("node:assert/strict");
const { test } = require("node:test");
const fs = require("node:fs");
const vm = require("node:vm");
const path = require("node:path");

const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");
const scripts = [...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/gi)]
  .map(match => match[1]);
assert.equal(scripts.length, 2, "theme initializer and solver script");

function openDemo(address) {
  const elements = new Map();
  const document = {
    documentElement: { dataset: {} },
    getElementById(id) {
      if (!elements.has(id)) {
        elements.set(id, {
          hidden: false, textContent: "", attributes: {},
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
  const context = vm.createContext({ document, window, URL, URLSearchParams });
  for (const script of scripts) vm.runInContext(script, context);
  return { document, window, changes, elements };
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
