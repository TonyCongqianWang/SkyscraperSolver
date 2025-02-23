import re
import sys

def find_max_nodes_visited(filepath):
    """
    Finds the maximum value for "Nodes visited" in a file.

    Args:
        filepath (str): The path to the input file.

    Returns:
        int: The maximum value of "Nodes visited", or None if no such value is found.
    """
    max_nodes_visited = None
    try:
        with open(filepath, 'r') as file:
            for line in file:
                match = re.search(r"Nodes visited: (\d+)", line)
                if match:
                    nodes_visited = int(match.group(1))
                    if max_nodes_visited is None or nodes_visited > max_nodes_visited:
                        max_nodes_visited = nodes_visited
    except FileNotFoundError:
        print(f"Error: File not found at {filepath}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    return max_nodes_visited

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <filepath>")
    else:
        filepath = sys.argv[1]
        max_value = find_max_nodes_visited(filepath)

        if max_value is not None:
            print(f"Maximum 'Nodes visited': {max_value}")
        else:
            print("No 'Nodes visited' values found or an error occurred.")