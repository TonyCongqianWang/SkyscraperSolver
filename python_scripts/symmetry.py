# Shared symmetry functions for Skyscraper solver benchmark scripts

def get_symmetries(T, B, L, R):
    """
    Returns the 8 symmetries of a clue set (T, B, L, R) under D_4.
    Each symmetry is returned as a 4-tuple of lists: (T_sym, B_sym, L_sym, R_sym).
    """
    T_lst = list(T)
    B_lst = list(B)
    L_lst = list(L)
    R_lst = list(R)

    s1 = (T_lst, B_lst, L_lst, R_lst)
    s2 = (L_lst[::-1], R_lst[::-1], B_lst, T_lst)
    s3 = (B_lst[::-1], T_lst[::-1], R_lst[::-1], L_lst[::-1])
    s4 = (R_lst, L_lst, T_lst[::-1], B_lst[::-1])
    s5 = (T_lst[::-1], B_lst[::-1], R_lst, L_lst)
    s6 = (R_lst[::-1], L_lst[::-1], B_lst[::-1], T_lst[::-1])
    s7 = (B_lst, T_lst, L_lst[::-1], R_lst[::-1])
    s8 = (L_lst, R_lst, T_lst, B_lst)
    return [s1, s2, s3, s4, s5, s6, s7, s8]

def get_symmetries_flat(T, B, L, R):
    """
    Returns the 8 symmetries as flat lists of length 4*N.
    """
    symmetries = get_symmetries(T, B, L, R)
    return [s[0] + s[1] + s[2] + s[3] for s in symmetries]

def canonize_one(T, B, L, R):
    """
    Computes the canonical representation of a clue set (T, B, L, R).
    Returns the lexicographically smallest flattened tuple of clues across all 8 symmetries.
    """
    flat_syms = get_symmetries_flat(T, B, L, R)
    return tuple(min(flat_syms))

def canonize_clue_str(clue_str):
    """
    Computes the canonical representation of a space-separated clue string.
    Returns the lexicographically smallest flattened tuple of clues across all 8 symmetries.
    """
    # Remove outer quotes if present
    clue_str = clue_str.strip('"\'')
    nums = list(map(int, clue_str.split()))
    return canonize_nums(nums)

def canonize_nums(nums):
    """
    Computes the canonical representation of a list/tuple of clues.
    Returns the lexicographically smallest flattened tuple of clues across all 8 symmetries.
    """
    n = len(nums) // 4
    T = nums[0:n]
    B = nums[n:2*n]
    L = nums[2*n:3*n]
    R = nums[3*n:4*n]
    return canonize_one(T, B, L, R)

def get_deduplicated_symmetries(clue_str):
    """
    Given a clue string (possibly wrapped in quotes), parses it,
    computes all 8 symmetries, deduplicates them, and returns them
    formatted in the same style (preserving quotes if the input had them).
    """
    clue_str = clue_str.strip()
    has_double_quotes = clue_str.startswith('"') and clue_str.endswith('"')
    has_single_quotes = clue_str.startswith("'") and clue_str.endswith("'")

    inner = clue_str.strip('"\'')
    nums = list(map(int, inner.split()))
    n = len(nums) // 4
    T = nums[0:n]
    B = nums[n:2*n]
    L = nums[2*n:3*n]
    R = nums[3*n:4*n]

    symmetries = get_symmetries_flat(T, B, L, R)

    seen = set()
    dedup = []
    for s in symmetries:
        t = tuple(s)
        if t not in seen:
            seen.add(t)
            s_str = " ".join(map(str, s))
            if has_double_quotes:
                s_str = f'"{s_str}"'
            elif has_single_quotes:
                s_str = f"'{s_str}'"
            dedup.append(s_str)
    return dedup

def deduplicate_dataset(clue_lines):
    """
    Deduplicates an iterable of clue strings modulo D_4 symmetry.
    Returns a list of unique clue strings, preserving the original string's formatting.
    """
    seen_canonical = set()
    deduped_lines = []

    for line in clue_lines:
        line_clean = line.strip()
        if not line_clean:
            continue

        # Compute the invariant canonical key for the current clue
        canon_key = canonize_clue_str(line_clean)

        # Keep only the first instance of any distinct puzzle orbit
        if canon_key not in seen_canonical:
            seen_canonical.add(canon_key)
            deduped_lines.append(line_clean)

    return deduped_lines
