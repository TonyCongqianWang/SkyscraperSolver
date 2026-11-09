const assert = require("node:assert/strict");
const { test } = require("node:test");
const { selectVersions } = require("./release_versions.cjs");

const release = (tag, date, prerelease = false, draft = false) => ({
  tag_name: tag, published_at: date, prerelease, draft,
});
const stable = release("v1.0.0", "2026-11-09T12:00:00Z");
const newer = release("v1.1.0-rc.1", "2026-11-10T12:00:00Z", true);
const older = release("v0.9.1", "2026-11-08T12:00:00Z", true);

test("stable is the default, with only the newest later prerelease offered", () => {
  const result = selectVersions([older, newer, stable], stable);
  assert.equal(result.default, "release");
  assert.deepEqual(result.versions.map(v => v.tag), ["v1.0.0", "v1.1.0-rc.1"]);
  assert.deepEqual(result.versions.map(v => v.path), ["release/solver.js", "prerelease/solver.js"]);
});

test("older or equally dated prereleases are omitted", () => {
  const equal = release("v1.0.0-rc.1", stable.published_at, true);
  for (const candidate of [older, equal]) {
    assert.deepEqual(selectVersions([candidate], stable).versions.map(v => v.tag), [stable.tag_name]);
  }
});

test("GitHub's designated latest stable is retained regardless of list ordering", () => {
  const different = release("v0.8.1", "2026-11-11T12:00:00Z");
  assert.equal(selectVersions([different, stable], stable).versions[0].tag, "v1.0.0");
});

test("prerelease-only repositories default to the most recently published prerelease", () => {
  const draft = release("v2.0.0-rc.1", "2026-11-12T12:00:00Z", true, true);
  const result = selectVersions([older, newer, draft], null);
  assert.equal(result.default, "prerelease");
  assert.deepEqual(result.versions.map(v => v.tag), [newer.tag_name]);
});

test("no published versions produces a clear deployment error", () => {
  assert.throws(() => selectVersions([], null), /No published release or prerelease/);
  assert.throws(() => selectVersions([release("draft", null, true, true)], null), /No published/);
});
