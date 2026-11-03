const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { pathToFileURL } = require("node:url");

(async () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "skyscraper-api-"));
  try {
    const modulePath = path.join(dir, "puzzles.mjs");
    fs.copyFileSync(path.join(__dirname, "puzzles.js"), modulePath);
    const metadata = {
      schema_version: 1, curated_version: "v1",
      difficulties: ["easy", "hard"],
      sizes: { "4": { easy: 2, hard: 0 }, "5": { easy: 0, hard: 1 } }
    };
    const puzzle = (n, id) => ({
      id, clues: Array(4 * n).fill(0),
      givens: Array(n * n).fill(0), canonical_solution: Array(n * n).fill(1),
      nodes_visited: 55, main_nodes_visited: 1,
      clue_count: 0, given_count: 0, minimal_puzzle_id: "base"
    });
    const datasets = {
      "metadata.json": metadata,
      "4/easy.json": { size: 4, difficulty: "easy", curated_version: "v1", schema_version: 1,
        source_bank: "unique/v1/minimal", difficulty_policy: "test",
        puzzles: [puzzle(4, "s4-p1:sample_a"), puzzle(4, "s4-p2:sample_b")] },
      "5/hard.json": { size: 5, difficulty: "hard", curated_version: "v1", schema_version: 1,
        source_bank: "unique/v1/minimal", difficulty_policy: "test",
        puzzles: [puzzle(5, "s5-p1:sample_c")] }
    };
    const calls = [];
    global.fetch = async url => {
      const pathname = new URL(url).pathname;
      const key = pathname.replace(/^.*\/curated\/v1\//, "");
      calls.push(key);
      return { ok: Boolean(datasets[key]), status: datasets[key] ? 200 : 404,
        json: async () => datasets[key] };
    };
    const { getRandomPuzzle, getPuzzleById, getMetadata } =
      await import(pathToFileURL(modulePath).href);
    const originalRandom = Math.random;
    try {
      Math.random = () => 0.1;
      const picked = await getRandomPuzzle({ size: 4, difficulty: "easy" });
      assert.equal(picked.size, 4);
      assert.equal(picked.puzzle_id, "v1:4:easy:s4-p1:sample_a");
      assert.equal(picked.id, "s4-p1:sample_a");
      assert.equal(picked.minimal_puzzle_id, "base");
      assert.deepEqual(await getPuzzleById(picked.puzzle_id), picked);
      assert.equal((await getPuzzleById("v1:4:easy:s4-p2:sample_b")).id, "s4-p2:sample_b");
      assert.equal(calls.filter(x => x === "4/easy.json").length, 1);
      Math.random = () => 0.99;
      const selection = await getRandomPuzzle();
      assert.equal(selection.size, 5);
      assert.equal(selection.difficulty, "hard");
      assert.equal(selection.puzzle_id, "v1:5:hard:s5-p1:sample_c");
      assert.equal((await getMetadata()).sizes["5"].hard, 1);
      assert.equal(calls.filter(x => x === "metadata.json").length, 1);
      await assert.rejects(getRandomPuzzle({ size: 3 }), RangeError);
      await assert.rejects(getRandomPuzzle({ difficulty: "unknown" }), RangeError);
      await assert.rejects(getRandomPuzzle({ size: 4, difficulty: "hard" }), RangeError);
      await assert.rejects(getPuzzleById("v2:4:easy:s4-p1:sample_a"), RangeError);
      await assert.rejects(getPuzzleById("v1:4:unknown:s4-p1:sample_a"), RangeError);
      await assert.rejects(getPuzzleById("v1:4:easy:missing"), RangeError);
      await assert.rejects(getPuzzleById("malformed"), RangeError);
      assert.equal(calls.filter(x => x === "metadata.json").length, 1);
      assert.equal(calls.filter(x => x === "4/easy.json").length, 1);
    } finally {
      Math.random = originalRandom;
    }
    console.log("Random puzzle and ID lookup tests passed");
  } finally {
    fs.rmSync(dir, { recursive: true, force: true });
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
