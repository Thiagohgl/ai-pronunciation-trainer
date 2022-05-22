import numpy as np

# ref from https://gitlab.com/-/snippets/1948157
# For some variants, look here https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Levenshtein_distance#Python

# Pure python
def edit_distance_python2(a, b):
    # This version is commutative, so as an optimization we force |a|>=|b|
    if len(a) < len(b):
        return edit_distance_python(b, a)
    if len(b) == 0:  # Can deal with empty sequences faster
        return len(a)
    # Only two rows are really needed: the one currently filled in, and the previous
    distances = []
    distances.append([i for i in range(len(b)+1)])
    distances.append([0 for _ in range(len(b)+1)])
    # We can prefill the first row:
    costs = [0 for _ in range(3)]
    for i, a_token in enumerate(a, start=1):
        distances[1][0] += 1  # Deals with the first column.
        for j, b_token in enumerate(b, start=1):
            costs[0] = distances[1][j-1] + 1
            costs[1] = distances[0][j] + 1
            costs[2] = distances[0][j-1] + (0 if a_token == b_token else 1)
            distances[1][j] = min(costs)
        # Move to the next row:
        distances[0][:] = distances[1][:]
    return distances[1][len(b)]

#https://stackabuse.com/levenshtein-distance-and-text-similarity-in-python/
def edit_distance_python(seq1, seq2):
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
    #print (matrix)
    return (matrix[size_x - 1, size_y - 1])