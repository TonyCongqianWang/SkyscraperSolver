#!/usr/bin/env python3
"""Compatibility entrypoint; implementation lives in dataset_generation."""
from dataset_generation.generator import (  # noqa: F401
    extract_clues_batch, generate_random_latin_square,
    generate_uniform_latin_squares, generate_unique_instances, main,
)

if __name__ == '__main__':
    main()
