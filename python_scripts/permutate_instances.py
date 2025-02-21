import re, sys

def reverse_numbers_in_line(line):
    """Reverses the numbers within the quoted string of a line."""
    match = re.search(r'"([^"]*)"', line)
    if match:
        numbers_str = match.group(1)
        numbers = numbers_str.split()
        reversed_numbers = numbers[::-1]
        reversed_numbers_str = " ".join(reversed_numbers)
        return line.replace(numbers_str, reversed_numbers_str)
    return line

def shift_numbers(line, shift_amount):
    """Shifts the numbers to the left by shift_amount spots."""
    match = re.search(r'"([^"]*)"', line)
    if match:
        numbers_str = match.group(1)
        numbers = numbers_str.split()
        shifted_numbers = numbers[shift_amount:] + numbers[:shift_amount]
        shifted_numbers_str = " ".join(shifted_numbers)
        return line.replace(numbers_str, shifted_numbers_str)
    return line

def shift_numbers_two_cycles(line, shift_amount):
    """Shifts numbers with two cycles of half the size, reversing the second half."""
    match = re.search(r'"([^"]*)"', line)
    if match:
        numbers_str = match.group(1)
        numbers = numbers_str.split()
        n = len(numbers)
        half_shift = shift_amount % n // 2

        # First half-cycle (same as before)
        first_half = numbers[:n//2]
        shifted_first_half = first_half[half_shift:] + first_half[:half_shift]

        # Second half-cycle (with reversal)
        second_half = numbers[n//2:]
        shifted_second_half = second_half[half_shift:] + second_half[:half_shift]
        shifted_second_half.reverse()  # Reverse the second half

        shifted_numbers = shifted_first_half + shifted_second_half
        shifted_numbers_str = " ".join(shifted_numbers)
        return line.replace(numbers_str, shifted_numbers_str)
    return line

def process_file(filename):
    """Processes a file, reversing numbers and appending to a new file."""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return

    shifted_lines1 = [shift_numbers(line, 14) for line in lines]
    shifted_lines2 = [shift_numbers_two_cycles(line, 14) for line in lines]
    shifted_lines3 = [shift_numbers_two_cycles(line, 14) for line in shifted_lines1]

    output_filename = filename + ".reversed"  # Create a new output filename
    try:
        with open(output_filename, 'w') as outfile:
            for original_line, shifted_line1, shifted_line2, shifted_line3 in zip(lines, shifted_lines1, shifted_lines2, shifted_lines3):
                outfile.write(original_line) # Write the original line first
                outfile.write(shifted_line1)   # Then the permutated line
                outfile.write(shifted_line2)   # Then the permutated line
                outfile.write(shifted_line3)   # Then the permutated line
                outfile.write(reverse_numbers_in_line(original_line)) # Write the original line first
                outfile.write(reverse_numbers_in_line(shifted_line1))  # Then the permutated line
                outfile.write(reverse_numbers_in_line(shifted_line2))   # Then the permutated line
                outfile.write(reverse_numbers_in_line(shifted_line3))   # Then the permutated line
                outfile.write("\n")        # Newline


        print(f"Reversed content written to '{output_filename}' successfully.")
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:  # Check if a filename argument is provided
        filename = sys.argv[1]
        process_file(filename)
    else:
        print("Error: Please provide a filename as a command-line argument.")
        print("Usage: python reverse_numbers.py <filename>")