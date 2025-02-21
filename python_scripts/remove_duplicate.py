def remove_duplicates(filename):
    """Removes duplicate lines from a file."""
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()

        unique_lines = list(dict.fromkeys(lines)) #remove dups, preserve order

        with open(filename, 'w') as f:
            f.writelines(unique_lines)

        print(f"Duplicates removed from {filename}.")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python remove_duplicates.py <filename>")
    else:
        filename = sys.argv[1]
        remove_duplicates(filename)