import numpy as np
import sys

def generate_latin_square_numpy(size, seed=None):
    """
    Generates a more randomized Latin square of a given size using NumPy.

    Args:
        size (int): The size of the Latin square (number of rows and columns).
        seed (int, optional): An optional seed for the NumPy random number generator.

    Returns:
        numpy.ndarray: A 2D NumPy array representing the Latin square, or None if size is invalid.
    """
    if not isinstance(size, int) or size <= 0 or size > 9:
        return None  # Invalid size

    if seed is not None:
        np.random.seed(seed)

    square = np.zeros((size, size), dtype=int)

    # Initialize the first row with a random permutation of numbers
    first_row = np.arange(size)
    np.random.shuffle(first_row)
    square[0] = first_row

    # Fill in the rest of the rows using a simple cyclic shift
    for i in range(1, size):
        square[i] = np.roll(square[i - 1], -1)

    # Shuffle rows (excluding the first row, which is already random)
    rows_to_shuffle = np.arange(1, size)
    np.random.shuffle(rows_to_shuffle)
    shuffled_square = np.concatenate(([square[0]], square[rows_to_shuffle]))

    # Shuffle columns
    columns_to_shuffle = np.arange(size)
    np.random.shuffle(columns_to_shuffle)
    final_square = shuffled_square[:, columns_to_shuffle]
    final_square += np.ones(final_square.shape, dtype=int)
    return final_square

def randomize_cells(square, seed=None, max_defects=3):
    """
    Randomly selects 'm' cells in the square and changes their values to random numbers within the range(1, dimension+1).

    Args:
        square: A 2D NumPy array representing the square.
        seed: an optional seed for the random number generator.

    Returns:
        A new 2D NumPy array with the specified elements randomized.
    """
    if seed is not None:
        np.random.seed(seed)

    if not isinstance(square, np.ndarray) or square.ndim != 2:
        raise ValueError("Square must be a 2D NumPy array.")

    new_square = square.copy()  # Create a copy to avoid modifying the original array

    # Determine the number of cells to change randomly
    m = np.random.randint(1, max_defects)  # Randomly select m between 1 and the total number of cells

    # Generate random indices for the cells to change
    indices = np.random.choice(square.size, size=m, replace=False)

    # Change the values of the selected cells
    for idx in indices:
        row, col = np.unravel_index(idx, square.shape)
        new_square[row, col] = np.random.randint(1, square.shape[0] + 1)

    return new_square

def count_visible_numbers_both_sides(square):
    """
    Counts the number of "visible" numbers in each row and column from both sides.

    Args:
        square: A 2D NumPy array representing the square.

    Returns:
        A tuple containing:
          - A list of tuples, where each inner tuple contains the visible counts for a row (left-to-right, right-to-left).
          - A list of tuples, where each inner tuple contains the visible counts for a column (top-to-bottom, bottom-to-top).
    """

    num_rows, num_cols = square.shape

    row_visibility = []
    col_visibility = []

    # Count visible numbers in each row from both sides
    for row in square:
        # Left-to-right
        left_to_right = 1
        max_so_far = row[0]
        for num in row[1:]:
            if num > max_so_far:
                left_to_right += 1
                max_so_far = num

        # Right-to-left
        right_to_left = 1
        max_so_far = row[-1]
        for num in reversed(row[:-1]):
            if num > max_so_far:
                right_to_left += 1
                max_so_far = num

        row_visibility.append((left_to_right, right_to_left))

    # Count visible numbers in each column from both sides
    for col_idx in range(num_cols):
        col = square[:, col_idx]

        # Top-to-bottom
        top_to_bottom = 1
        max_so_far = col[0]
        for num in col[1:]:
            if num > max_so_far:
                top_to_bottom += 1
                max_so_far = num

        # Bottom-to-top
        bottom_to_top = 1
        max_so_far = col[-1]
        for num in reversed(col[:-1]):
            if num > max_so_far:
                bottom_to_top += 1
                max_so_far = num

        col_visibility.append((top_to_bottom, bottom_to_top))

    return row_visibility, col_visibility

# Example usage:
if __name__ == "__main__":
    try:
      size = int(sys.argv[1])
    except:
      size = 4
    try:
      count = int(sys.argv[2])
    except:
      count = 1

    latin_squares = []
    formatted_outputs = []

    for _ in range(count):
      latin_square = generate_latin_square_numpy(size)
      latin_square = randomize_cells(latin_square, max_defects=5)
      row_visibility, col_visibility = count_visible_numbers_both_sides(latin_square)
    
      formatted_output = [str(a) for (a, b) in col_visibility] + [str(b) for (a, b) in col_visibility]
      formatted_output += [str(a) for (a, b) in row_visibility] + [str(b) for (a, b) in row_visibility]
      formatted_output = "skyscraper_solver \"" + " ".join(formatted_output) + "\""

      if formatted_output not in formatted_outputs:
        latin_squares.append(latin_square)
        formatted_outputs.append(formatted_output)

    with open("tmp.txt", "w") as f:
      for latin_square in latin_squares:
        print(latin_square, file=f)
      for formatted_output in formatted_outputs:
        print(formatted_output, file=f)
