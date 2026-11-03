/** Static, browser-side curated puzzle API. */
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
      !metadata.sizes || typeof metadata.sizes !== "object" ||
      typeof metadata.curated_version !== "string") {
    throw new Error("Invalid puzzle metadata");
  }
  return metadata;
}

function parsePuzzleId(puzzleId) {
  // The final component is the original record ID and may itself contain colons.
  const match = typeof puzzleId === "string" &&
    /^([^:]+):([4-9]):([a-z_]+):(.+)$/.exec(puzzleId);
  if (!match || match[1] !== "v1") {
    throw new RangeError("Invalid or unsupported puzzle ID");
  }
  return { version: match[1], size: Number(match[2]),
    difficulty: match[3], originalId: match[4] };
}

async function readShard(metadata, size, difficulty) {
  const count = metadata.sizes[String(size)]?.[difficulty] ?? 0;
  if (!Number.isSafeInteger(count) || count < 0) {
    throw new Error("Invalid puzzle count");
  }
  if (!count) {
    throw new RangeError("No curated puzzles for this size and difficulty");
  }
  const shard = await readJSON(size + "/" + difficulty + ".json");
  if (shard?.size !== size || shard?.difficulty !== difficulty ||
      !Array.isArray(shard.puzzles) || shard.puzzles.length !== count ||
      shard.curated_version !== metadata.curated_version) {
    throw new Error("Curated shard does not match metadata");
  }
  return shard;
}

function completePuzzle(shard, puzzle) {
  const { size, difficulty } = shard;
  if (!puzzle || typeof puzzle.id !== "string" || !puzzle.id ||
      !Array.isArray(puzzle.clues) || puzzle.clues.length !== 4 * size ||
      !Array.isArray(puzzle.givens) || puzzle.givens.length !== size ** 2 ||
      !Array.isArray(puzzle.canonical_solution) ||
      puzzle.canonical_solution.length !== size ** 2) {
    throw new Error("Invalid curated puzzle record");
  }
  return {
    ...puzzle,
    puzzle_id: shard.curated_version + ":" + size + ":" + difficulty + ":" + puzzle.id,
    size,
    difficulty,
    curated_version: shard.curated_version,
    schema_version: shard.schema_version,
    source_bank: shard.source_bank,
    difficulty_policy: shard.difficulty_policy,
  };
}

/**
 * Choose uniformly from matching curated puzzles (with replacement).
 * Specify size, difficulty, both, or neither. Only the selected shard is
 * downloaded; successful fetches and in-flight requests are cached.
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
        choices.push({ size: Number(sizeText), difficulty: level, cumulative: total });
      }
    }
  }
  if (!total) throw new RangeError("No curated puzzles for the requested filters");
  const ticket = Math.floor(Math.random() * total);
  const selected = choices.find(choice => ticket < choice.cumulative);
  const shard = await readShard(metadata, selected.size, selected.difficulty);
  return completePuzzle(shard, shard.puzzles[Math.floor(Math.random() * shard.puzzles.length)]);
}

/**
 * Resolve a version-tagged puzzle ID using only its size/difficulty shard.
 * Example: v1:7:extreme_plus:s7-00001-p001:sample_abc123
 */
export async function getPuzzleById(puzzleId) {
  const parsed = parsePuzzleId(puzzleId);
  const metadata = await getMetadata();
  if (parsed.version !== metadata.curated_version ||
      !metadata.difficulties.includes(parsed.difficulty)) {
    throw new RangeError("Invalid or unsupported puzzle ID");
  }
  const shard = await readShard(metadata, parsed.size, parsed.difficulty);
  const puzzle = shard.puzzles.find(entry => entry.id === parsed.originalId);
  if (!puzzle) throw new RangeError("Puzzle ID not found");
  return completePuzzle(shard, puzzle);
}
