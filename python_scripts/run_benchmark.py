import subprocess
import sys
import time
from datetime import datetime
import shlex
import statistics
import os
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.append(SCRIPT_DIR)

from symmetry import deduplicate_dataset


def format_time(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds)) + f".{int(seconds * 1000) % 1000:03d}"


def parse_duration(s):
    """Parse a duration string into total seconds (float).

    Supported formats:  hh:mm:ss  |  mm:ss  |  Xs / Xm / Xh  |  plain number
    Returns None when s is None.
    """
    if s is None:
        return None
    s = s.strip()

    # hh:mm:ss or mm:ss via strptime
    for fmt, multipliers in [
        ("%H:%M:%S", (3600, 60, 1)),
        ("%M:%S",    (60, 1)),
    ]:
        try:
            t = datetime.strptime(s, fmt)
            parts = (t.hour, t.minute, t.second) if len(multipliers) == 3 \
                    else (t.minute, t.second)
            return sum(p * m for p, m in zip(parts, multipliers))
        except ValueError:
            pass

    # Xs / Xm / Xh shorthand
    suffixes = {'s': 1, 'm': 60, 'h': 3600}
    if s and s[-1].lower() in suffixes:
        try:
            return float(s[:-1]) * suffixes[s[-1].lower()]
        except ValueError:
            pass

    # plain number (seconds)
    try:
        return float(s)
    except ValueError:
        pass

    raise ValueError(
        f"Cannot parse duration: {s!r}. "
        "Use hh:mm:ss, mm:ss, 10m, 90s, 2h, or a plain number of seconds."
    )


def main(command_name, filename, output_file=None, options="",
         time_limit=None, print_period=None, use_stdin=False, print_summary_limit=-1,
         include_symmetries=False):
    try:
        with open(filename, 'r') as file:
            raw_lines = file.readlines()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    lines = [l.strip() for l in raw_lines if l.strip()]
    lines = deduplicate_dataset(lines, include_symmetries)

    total = len(lines)

    if output_file and os.path.exists(output_file):
        print(f"Error: Output file {output_file} already exists.")
        return

    # --print-time-period semantics:
    #   None  -> always print everything (default / current behaviour)
    #   <= 0  -> silence all instance output; only print final summary to stdout
    #   > 0   -> print a brief periodic status line; suppress per-instance detail
    always_print = print_period is None
    silent_all   = (print_period is not None) and (print_period <= 0)
    periodic     = (print_period is not None) and (print_period > 0)
    # Trigger the first periodic print immediately when the first instance finishes
    last_print_t = time.time() - (print_period if periodic else 0)

    if output_file:
        output_f = open(output_file, 'w')
    else:
        output_f = None

    def fwrite(data):
        if output_f:
            output_f.write(data)
            output_f.flush()

    def stdout_write(data):
        sys.stdout.write(data)
        sys.stdout.flush()

    def write_instance(data):
        """Write to file always; write to stdout only in always_print mode."""
        fwrite(data)
        if always_print:
            stdout_write(data)

    def write_summary(data):
        """Always write to both file and stdout (final summary)."""
        fwrite(data)
        stdout_write(data)

    elapsed_times      = []
    commands           = []
    nodes_visited_list = []
    total_start_time   = time.time()
    total_start_dt     = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    time_limit_reached = False

    interactive_process = None
    if use_stdin:
        base_args = shlex.split(options)
        if "--stdin" not in base_args:
            base_args.append("--stdin")
        try:
            interactive_process = subprocess.Popen(
                [command_name] + base_args,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
            )
        except FileNotFoundError:
            interactive_process = subprocess.Popen(
                ["./" + command_name] + base_args,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
            )

    for idx, line in enumerate(lines, start=1):
        # Check time limit before starting this instance
        if time_limit is not None and (time.time() - total_start_time) >= time_limit:
            time_limit_reached = True
            break

        # Progress counter — always goes to file; stdout depends on mode
        progress_line = f"Instance {idx} / {total}\n"
        fwrite(progress_line)
        if always_print:
            stdout_write(progress_line)

        time_format = "%H:%M:%S.%f"
        start_time  = time.time()

        if use_stdin:
            try:
                # Ensure the exact raw file string line is forwarded down the pipe
                interactive_process.stdin.write(line + "\n")
                interactive_process.stdin.flush()
            except BrokenPipeError:
                hidden_error = interactive_process.stderr.read()
                print(f"\n[CRITICAL] Solver crashed! Hidden Traceback:\n{hidden_error}", file=sys.stderr)
                break
            # 2. Wait for the output or EOF
            out_lines = []
            while True:
                out_line = interactive_process.stdout.readline()
                if not out_line or "--- END_OF_INSTANCE ---" in out_line:
                    break
                out_lines.append(out_line)

            stdout = "".join(out_lines)
            stderr = ""
            command = f"{command_name} {options} <stdin> {line}"

            # 3. Check if the process died while computing this specific instance
            if interactive_process.poll() is not None:
                stderr = interactive_process.stderr.read()
                print(f"\n[CRITICAL] Solver died during execution! Traceback:\n{stderr}", file=sys.stderr)
                break
        else:
            args = shlex.split(options) + shlex.split(line)
            try:
                process = subprocess.Popen(
                    [command_name] + args,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
            except FileNotFoundError:
                command_name = "./" + command_name
                process = subprocess.Popen(
                    [command_name] + args,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
                )
            stdout, stderr = process.communicate()
            parts = [command_name]
            if options:
                parts.append(options)
            parts.append(line)
            command = " ".join(parts)

        elapsed_time = time.time() - start_time
        elapsed_times.append(elapsed_time)
        commands.append(command)

        nodes_visited = 0
        for line_out in stdout.splitlines():
            if line_out.startswith("Nodes visited:"):
                try:
                    nodes_visited = int(line_out.split(":")[1].strip())
                except ValueError:
                    pass
        nodes_visited_list.append(nodes_visited)

        instance_block = (
            f"\nCommand: {command}\n"
            + (f"Input: {line}\n\n" if use_stdin else "\n") +
            f"{stdout}"
            f"{stderr}"
            f"Elapsed: {format_time(elapsed_time)}\n"
        )
        write_instance(instance_block)

        # Periodic status line to stdout
        if periodic:
            now = time.time()
            if now - last_print_t >= print_period:
                last_print_t = now
                total_elapsed = now - total_start_time
                stdout_write(
                    f"[{datetime.now().strftime('%H:%M:%S')}] "
                    f"Progress: {idx}/{total} instances | "
                    f"Elapsed: {format_time(total_elapsed)}\n"
                )

    if interactive_process:
        interactive_process.stdin.close()
        interactive_process.terminate()

    total_end_dt = datetime.now().strftime("%H:%M:%S.%f")[:-3]

    # ── Time-limit notification ───────────────────────────────────────────────
    if time_limit_reached:
        write_summary(
            f"\n*** Time limit reached ({format_time(time_limit)}) ***\n"
            f"Instances solved: {len(elapsed_times)} / {total}\n"
        )

    # ── Statistics ───────────────────────────────────────────────────────────
    if elapsed_times:
        mean_time   = statistics.mean(elapsed_times)
        median_time = statistics.median(elapsed_times)
        max_time    = max(elapsed_times)
        total_time  = sum(elapsed_times)

        mean_nodes   = statistics.mean(nodes_visited_list)   if nodes_visited_list else 0
        median_nodes = statistics.median(nodes_visited_list) if nodes_visited_list else 0
        max_nodes    = max(nodes_visited_list)               if nodes_visited_list else 0
        total_nodes  = sum(nodes_visited_list)               if nodes_visited_list else 0

        write_summary(f"\nSorted Times:\n\n")
        sorted_cmds_times = sorted(zip(commands, elapsed_times), key=lambda x: x[1])
        for i, (cmd, et) in enumerate(sorted_cmds_times):
            if print_summary_limit >= 0 and i >= len(sorted_cmds_times) - print_summary_limit:
                write_summary(f"Command: {cmd}\n")
                write_summary(f"Elapsed: {format_time(et)}\n\n")
            else:
                fwrite(f"Command: {cmd}\n")
                fwrite(f"Elapsed: {format_time(et)}\n\n")

        write_summary(f"\nStart: {total_start_dt}\n")
        write_summary(f"End: {total_end_dt}\n")
        write_summary("\nTotal Time Statistics:\n")
        write_summary(f"Mean: {format_time(mean_time)}\n")
        write_summary(f"Median: {format_time(median_time)}\n")
        write_summary(f"Max: {format_time(max_time)}\n")
        write_summary(f"Total: {format_time(total_time)}\n")

        write_summary("\nTotal Nodes Visited Statistics:\n")
        write_summary(f"Mean: {mean_nodes:.2f}\n")
        write_summary(f"Median: {median_nodes:.2f}\n")
        write_summary(f"Max: {max_nodes}\n")
        write_summary(f"Total: {total_nodes}\n")

    # ── Trailing time-limit warning ───────────────────────────────────────────
    if time_limit_reached:
        write_summary(
            f"\nNote: Only {len(elapsed_times)}/{total} instances were solved "
            "due to the time limit. Statistics above may not be representative "
            "of the full benchmark.\n"
        )

    if output_f:
        output_f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run benchmark for skyscraper_solver.')
    parser.add_argument('filename', help='Input file with command line arguments')
    parser.add_argument('-f', '--options', default="", help='Extra arguments for command')
    parser.add_argument('-o', '--output', help='Output file to save results')
    parser.add_argument('-c', '--command', default='skyscraper_solver',
                        help='Command name to run')
    parser.add_argument('--time-limit', default=None,
                        help='Stop after this duration (e.g. 10m, 1h30m, 01:30:00). '
                             'Prints a warning and partial stats when reached.')
    parser.add_argument('--print-time-period', default=None,
                        help='How often to print progress to stdout (e.g. 30s, 1m). '
                             'Instance output is silenced between prints. '
                             '0 or negative silences everything except the final summary. '
                             'Omit for continuous real-time output (default). '
                             'Does not affect output written with -o.')
    parser.add_argument('--print-limit-summary', default=10, type=int,
                        help='Maximum number of instance to print at summary. Negative value to print all.')
    parser.add_argument('--use-stdin', action='store_true', default=True,
                        help='Pass the puzzle input via stdin interactively (enabled by default).')
    parser.add_argument('--no-use-stdin', action='store_false', dest='use_stdin',
                        help='Disable stdin batching and run instances as individual subprocesses.')
    parser.add_argument('--all-sols', action='store_true',
                        help='Enumerate all solutions (applies -s 0 to the solver options).')
    parser.add_argument('--include-symmetries', action='store_true', dest='include_symmetries', default=None,
                        help='Solve all deduplicated symmetries of each instance to reduce variance.')
    parser.add_argument('--no-include-symmetries', action='store_false', dest='include_symmetries', default=None,
                        help='Disable solving all symmetries of each instance.')

    args = parser.parse_args()

    # Determine default for include_symmetries based on all_sols
    if args.include_symmetries is None:
        if args.all_sols:
            include_symmetries = False
        else:
            include_symmetries = True
    else:
        include_symmetries = args.include_symmetries

    # Prepend "-s 0" to options if all_sols is requested
    options = args.options
    if args.all_sols:
        if options.strip():
            options = "-s 0 " + options
        else:
            options = "-s 0"

    try:
        time_limit   = parse_duration(args.time_limit)
        print_period = parse_duration(args.print_time_period)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    main(args.command, args.filename, args.output, options,
         time_limit=time_limit, print_period=print_period, use_stdin=args.use_stdin,
         print_summary_limit=args.print_limit_summary, include_symmetries=include_symmetries)
