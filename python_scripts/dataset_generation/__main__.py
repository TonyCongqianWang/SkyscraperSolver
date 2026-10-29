"""CLI: python3 -m python_scripts.dataset_generation COMMAND --help."""
import argparse
import math
from pathlib import Path
import sys

from .common import ROOT


def parser():
    command = argparse.ArgumentParser(description='Portable SPSA dataset generation and installation')
    subcommands = command.add_subparsers(dest='command', required=True)
    generate = subcommands.add_parser('generate', help='Generate fresh symmetry-unique candidate puzzles')
    generate.add_argument('--size', '-n', type=int, required=True)
    generate.add_argument('--count', '-c', type=int, default=10000)
    generate.add_argument('--output', '-o', type=Path, required=True)
    generate.add_argument('--seed', type=int, default=20261029)
    generate.add_argument('--burn-in', type=int, default=100000)
    generate.add_argument('--gap', type=int, default=100)
    run = subcommands.add_parser('run', help='Resume/build, verify, and bundle SPSA datasets; never install')
    run.add_argument('--sizes', type=int, nargs='+', choices=(8, 9), default=[8, 9])
    run.add_argument('--train-count', type=int, default=10000)
    run.add_argument('--validation-count', type=int, default=1000)
    run.add_argument('--difficulty-mix', type=float, nargs=3, metavar=('EASY', 'MEDIUM', 'HARD'), default=[.2, .5, .3])
    run.add_argument('--seed', type=int, default=20261029)
    run.add_argument('--max-workers', type=int, default=4)
    run.add_argument('--timeout', type=float, default=8.0)
    run.add_argument('--recheck-threshold', type=float, default=6.4)
    run.add_argument('--reference-count', type=int, default=500)
    run.add_argument('--candidate-batch-size', type=int, default=2000)
    run.add_argument('--burn-in', type=int, default=100000)
    run.add_argument('--gap', type=int, default=100)
    run.add_argument('--max-batches', type=int, default=1000, help='Stop without activating partial results if quotas remain unfilled')
    run.add_argument('--solver', type=Path, default=ROOT / 'skyscraper_solver')
    run.add_argument('--work-dir', type=Path, default=ROOT / 'scratch/spsa_dataset_generation')
    for name in ('verify', 'install'):
        selected = subcommands.add_parser(name, help='Verify results' if name == 'verify' else 'Archive and activate verified results')
        selected.add_argument('results', type=Path, help='Results directory or .tar.gz bundle')
        if name == 'install':
            selected.add_argument('--destination', type=Path, default=ROOT / 'puzzle_bank/spsa_datasets')
    return command


def validate(args):
    if args.command == 'generate':
        if not 2 <= args.size <= 9 or args.count < 1 or args.burn_in < 0 or args.gap < 1:
            raise ValueError('size must be 2..9, count/gap positive, burn-in nonnegative')
    if args.command == 'run':
        from .difficulty import quotas
        if len(set(args.sizes)) != len(args.sizes):
            raise ValueError('Duplicate sizes are not allowed')
        args.sizes = sorted(args.sizes)
        if (any(not math.isfinite(weight) or weight < 0 for weight in args.difficulty_mix) or
                not math.isclose(sum(args.difficulty_mix), 1.0, abs_tol=1e-10)):
            raise ValueError('Difficulty proportions must be nonnegative and sum to one')
        if (min(args.train_count, args.validation_count, args.max_workers, args.candidate_batch_size,
                args.gap, args.max_batches) < 1 or args.reference_count < 3 or args.burn_in < 0):
            raise ValueError('Counts/workers/gap/batches must be positive, references >=3, burn-in >=0')
        if (not math.isfinite(args.timeout) or not math.isfinite(args.recheck_threshold) or
                not 0 < args.recheck_threshold < args.timeout):
            raise ValueError('Require 0 < recheck threshold < timeout, both finite')
        quotas(args.train_count, args.validation_count, args.difficulty_mix)
        if not args.solver.is_file():
            raise ValueError('Solver is missing: build it with make or pass --solver')


def main(argv=None):
    command = parser()
    args = command.parse_args(argv)
    try:
        validate(args)
        if args.command == 'generate':
            from .generator import generate_unique_instances
            clues = generate_unique_instances(args.size, args.count, args.burn_in, args.gap, args.seed)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(''.join(f'"{clue}"\n' for clue in clues))
        elif args.command == 'run':
            from .pipeline import run
            run(args)
        elif args.command == 'verify':
            from .artifacts import verify
            verify(args.results)
        elif args.command == 'install':
            from .artifacts import install
            install(args.results, args.destination)
    except KeyboardInterrupt:
        return 130
    except (ValueError, OSError, RuntimeError, ImportError) as error:
        print(f'Error: {error}', file=sys.stderr)
        if isinstance(error, ImportError):
            print('Install dependencies: python3 -m pip install -r '
                  'python_scripts/dataset_generation/requirements.txt', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
