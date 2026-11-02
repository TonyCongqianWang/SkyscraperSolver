/** Browser-side curated puzzle API for GitHub Pages (no server runtime). */
const baseUrl = new URL("./", import.meta.url);
const DIFFICULTIES = ["very_easy","easy","medium","hard","very_hard","extreme","impossible"];
const cache = new Map();

async function readJSON(name) {
  if (!cache.has(name)) {
    const pending = fetch(new URL(name, baseUrl)).then(async response => {
      if (!response.ok) throw new Error(`Puzzle bank request failed (${response.status}): ${name}`);
      return response.json();
    });
    cache.set(name, pending);
    pending.catch(() => { if (cache.get(name) === pending) cache.delete(name); });
  }
  return cache.get(name);
}

export async function getMetadata() {
  const data = await readJSON("metadata.json");
  if (data.schema_version !== 1 || !data.sizes || typeof data.sizes !== "object") {
    throw new Error("Invalid curated puzzle metadata");
  }
  return data;
}

/**
 * Returns a curated puzzle with its original fields plus size and difficulty.
 * Repeated calls may select the same puzzle. Fetch failures reject, allowing
 * consumers to retry or fall back to their own local generator.
 */
export async function getRandomPuzzle({ size, difficulty }) {
  if (!Number.isInteger(size) || size < 4 || size > 9) throw new RangeError("size must be an integer from 4 to 9");
  if (!DIFFICULTIES.includes(difficulty)) throw new RangeError("Unknown difficulty");
  const metadata = await getMetadata();
  const count = metadata.sizes[String(size)]?.[difficulty] ?? 0;
  if (!Number.isSafeInteger(count) || count < 0) throw new Error("Invalid puzzle count in metadata");
  if (count === 0) throw new RangeError(`No curated puzzles for size ${size}, difficulty ${difficulty}`);
  const bank = await readJSON(`size_${size}.json`);
  const puzzles = bank?.difficulties?.[difficulty];
  if (bank?.size !== size || !Array.isArray(puzzles) || puzzles.length !== count) {
    throw new Error("Curated puzzle bank does not match metadata");
  }
  const puzzle = puzzles[Math.floor(Math.random() * puzzles.length)];
  if (!puzzle || !Array.isArray(puzzle.clues) || puzzle.clues.length !== 4 * size ||
      !Array.isArray(puzzle.givens) || puzzle.givens.length !== size * size ||
      !Array.isArray(puzzle.canonical_solution) || puzzle.canonical_solution.length !== size * size) {
    throw new Error("Invalid curated puzzle record");
  }
  return { ...puzzle, size, difficulty };
}
