import subprocess
import sys
import time
from datetime import datetime
import shlex
import statistics
import os
import argparse

def format_time(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds)) + f".{int(seconds * 100) % 100:02d}"

def main(command_name, filename, output_file=None, options=""):
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return

    if output_file and os.path.exists(output_file):
        print(f"Error: Output file {output_file} already exists.")
        return

    elapsed_times = []
    commands = []
    total_start_time = time.time()
    total_start_dt = datetime.now().strftime("%H:%M:%S.%f")[:-3]

    if output_file:
        output_f = open(output_file, 'w')
    else:
        output_f = None

    def write_output(data):
        print(data, end='', file=output_f)

    for line in lines:
        line = line.strip()
        time_format = "%H:%M:%S.%f"
        if line:
            start_time = time.time()
            start_dt = datetime.now().strftime(time_format)[:-3]

            args = shlex.split(options)
            args += shlex.split(line)
            process = subprocess.Popen([command_name] + args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            stdout, stderr = process.communicate()
            end_time = time.time()
            end_dt = datetime.now().strftime(time_format)[:-3]

            elapsed_time = end_time - start_time
            elapsed_times.append(elapsed_time)
            command = " ".join([command_name] + [options] + [line])
            commands.append(command)

            write_output("\n")
            write_output(f"Command: {command}\n")
            write_output("\n")
            write_output(stdout)
            write_output(stderr)
            write_output(f"Elapsed: {format_time(elapsed_time)}\n")

    total_end_time = time.time()
    total_end_dt = datetime.now().strftime("%H:%M:%S.%f")[:-3]

    if elapsed_times:
        mean_time = statistics.mean(elapsed_times)
        median_time = statistics.median(elapsed_times)
        max_time = max(elapsed_times)
        total_time = sum(elapsed_times)

        write_output(f"\nSorted Times:\n\n")
        for command, elapsed_time in sorted(zip(commands, elapsed_times), key=lambda x: x[1]):
          write_output(f"Command: {command}\n")
          write_output(f"Elapsed: {format_time(elapsed_time)}\n\n")

        write_output(f"\nStart: {total_start_dt}\n")
        write_output(f"End: {total_end_dt}\n")
        write_output("\nTotal Time Statistics:\n")
        write_output(f"Mean: {format_time(mean_time)}\n")
        write_output(f"Median: {format_time(median_time)}\n")
        write_output(f"Max: {format_time(max_time)}\n")
        write_output(f"Total: {format_time(total_time)}\n")

    if output_f:
        output_f.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run benchmark for skyscraper_solver.')
    parser.add_argument('filename', help='Input file with command line arguments')
    parser.add_argument('-f', '--options', default="", help='Extra arguments for command')
    parser.add_argument('-o', '--output', help='Output file to save results')
    parser.add_argument('-c', '--command', default='skyscraper_solver', help='Command name to run')

    args = parser.parse_args()

    main(args.command, args.filename, args.output, args.options)
