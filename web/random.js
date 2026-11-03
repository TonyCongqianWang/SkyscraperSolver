/** Static, browser-side random puzzle API. */
const root = new URL("./curated/v1/", import.meta.url);
const cache = new Map();

function readJSON(path) {
  if (!cache.has(path)) {
    const request = fetch(new URL(path, root)).then(async response => {
      if (!response.ok) throw new Error("Puzzle request failed (" + response.status + "): " + path);
      return response.json();
    });
    cache.set(path, request);
    request.catch(() => { if (cache.get(path) === request) cache.delete(path); });
  }
  return cache.get(path);
}

export async function getMetadata() {
  const metadata = await readJSON("metadata.json");
  if (metadata?.schema_version !== 1 || !Array.isArray(metadata.difficulties) ||
      !metadata.sizes || typeof metadata.sizes !== "object") {
    throw new Error("Invalid puzzle metadata");
  }
  return metadata;
}

/**
 * Choose uniformly from matching curated puzzles (with replacement).
 * Specify size, difficulty, both, or neither. Fetches and caches only the
 * selected size/difficulty shard. Rejects when unavailable.
 */
export async function getRandomPuzzle({ size, difficulty } = {}) {
  if (size !== undefined && (!Number.isInteger(size) || size < 4 || size > 9)) {
    throw new RangeError("size must be an integer from 4 to 9");
  }
  const metadata = await getMetadata();
  if (difficulty !== undefined && !metadata.difficulties.includes(difficulty)) {
    throw new RangeError("Unknown difficulty");
  }
  const choices = [];
  let total = 0;
  for (const [sizeText, levels] of Object.entries(metadata.sizes)) {
    if (size !== undefined && Number(sizeText) !== size) continue;
    for (const level of metadata.difficulties) {
      if (difficulty !== undefined && level !== difficulty) continue;
      const count = levels[level];
      if (!Number.isSafeInteger(count) || count < 0) throw new Error("Invalid puzzle count");
      if (count) {
        total += count;
        choices.push({ size: Number(sizeText), difficulty: level, count, cumulative: total });
      }
    }
  }
  if (!total) throw new RangeError("No curated puzzles for the requested filters");
  const ticket = Math.floor(Math.random() * total);
  const selected = choices.find(choice => ticket < choice.cumulative);
  const shard = await readJSON(selected.size + "/" + selected.difficulty + ".json");
  if (shard?.size !== selected.size || shard?.difficulty !== selected.difficulty ||
      !Array.isArray(shard.puzzles) || shard.puzzles.length !== selected.count ||
      shard.curated_version !== metadata.curated_version) {
    throw new Error("Curated shard does not match metadata");
  }
  const index = Math.floor(Math.random() * selected.count);
  const puzzle = shard.puzzles[index];
  if (!puzzle || !Array.isArray(puzzle.clues) || puzzle.clues.length !== 4 * selected.size ||
      !Array.isArray(puzzle.givens) || puzzle.givens.length !== selected.size ** 2 ||
      !Array.isArray(puzzle.canonical_solution) || puzzle.canonical_solution.length !== selected.size ** 2) {
    throw new Error("Invalid curated puzzle record");
  }
  return {
    ...puzzle,
    size: selected.size,
    difficulty: selected.difficulty,
    curated_version: shard.curated_version,
    schema_version: shard.schema_version,
    source_bank: shard.source_bank,
    difficulty_policy: shard.difficulty_policy,
  };
}
