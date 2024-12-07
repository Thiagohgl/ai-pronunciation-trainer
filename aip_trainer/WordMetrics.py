import numpy as np

from aip_trainer import app_logger


# https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
def edit_distance_python(seq1: str, seq2: str) -> np.ndarray:
    """
    Calculate the edit distance (Levenshtein distance) between two sequences.

    The edit distance is the minimum number of single-character edits (insertions, deletions, or substitutions)
    required to change one sequence into the other.

    Args:
        seq1 (str): The first sequence.
        seq2 (str): The second sequence.

    Returns:
        int: The edit distance between the two sequences.
    """
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in range(size_x):
        matrix [x, 0] = x
    for y in range(size_y):
        matrix [0, y] = y

    for x in range(1, size_x):
        for y in range(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    app_logger.debug("matrix:{}\n".format(matrix))
    return matrix[size_x - 1, size_y - 1]
