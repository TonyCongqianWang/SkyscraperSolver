"""Generate the unfiltered SPSA splits for the size-7 parameter group.

Run with python -m python_scripts.dataset_generation.le7.
"""

import random

from .common import ROOT
from .generator import (
    extract_clues_batch,
    generate_random_latin_square,
    generate_uniform_latin_squares,
    seed_mcmc,
)

DATASET_DIR = ROOT / 'puzzle_bank' / 'spsa_datasets'
TRAIN_COUNTS = {5: 10_000, 6: 50_000, 7: 200_000}
RESEED_INTERVAL = 100
SEED = 20261109


def generate_split(counts, seed):
    rng = random.Random(seed)
    clues = []
    for size, count in counts.items():
        for start in range(0, count, RESEED_INTERVAL):
            random.seed(rng.getrandbits(64))
            seed_mcmc(rng.getrandbits(32))
            grid = generate_random_latin_square(size)
            squares, _ = generate_uniform_latin_squares(
                size, min(RESEED_INTERVAL, count - start), grid
            )
            for sides in zip(*extract_clues_batch(squares)):
                clues.append(' '.join(str(value) for side in sides for value in side))
    rng.shuffle(clues)
    return clues


def main():
    for split, divisor, seed in (('train', 1, SEED), ('val', 10, SEED + 1)):
        clues = generate_split({size: count // divisor for size, count in TRAIN_COUNTS.items()}, seed)
        target = DATASET_DIR / f'le7_{split}.txt'
        temporary = target.with_suffix('.tmp')
        temporary.write_text(''.join(f'"{clue}"\n' for clue in clues), encoding='ascii')
        temporary.replace(target)
        print(f'Wrote {len(clues):,} instances to {target.relative_to(ROOT)}', flush=True)


if __name__ == '__main__':
    main()
