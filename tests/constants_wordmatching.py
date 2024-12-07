import numpy as np


get_best_path_from_distance_matrix_constants = [
    (np.array([[0, 4], [5, 1], [5, 4]]), np.array([0, 1])),
    (
        np.array([[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0], [1.0, 1.0, 1.0]]),
        np.array([0, 1, 2]),
    ),
    (
        np.array(
            [
                [2.0, 5.0, 5.0, 5.0, 5.0],
                [6.0, 0.0, 4.0, 3.0, 3.0],
                [6.0, 4.0, 0.0, 3.0, 4.0],
                [6.0, 3.0, 3.0, 0.0, 4.0],
                [6.0, 2.0, 4.0, 3.0, 1.0],
                [6.0, 3.0, 4.0, 2.0, 4.0],
            ]
        ),
        np.array([0, 1, 2, 3, 4]),
    ),
    (
        np.array(
            [
                [1.0, 6.0, 3.0, 3.0, 4.0],
                [5.0, 1.0, 4.0, 3.0, 5.0],
                [3.0, 5.0, 0.0, 3.0, 3.0],
                [3.0, 4.0, 3.0, 0.0, 4.0],
                [3.0, 6.0, 2.0, 3.0, 1.0],
                [2.0, 6.0, 3.0, 3.0, 4.0],
            ]
        ),
        np.array([0, 1, 2, 3, 4]),
    ),
    (
        np.array(
            [
                [0.0, 2.0, 3.0],
                [2.0, 0.0, 1.0],
                [3.0, 1.0, 0.0],
            ]
        ),
        np.array([0, 1, 1]),
    ),
    (
        np.array(
            [
                [0.0, 1.0, 2.0, 3.0],
                [1.0, 0.0, 1.0, 2.0],
                [2.0, 1.0, 0.0, 1.0],
                [3.0, 2.0, 1.0, 0.0],
            ]
        ),
        np.array([0, 1, 2, 2]),
    ),
    (
        np.array(
            [
                [0.0, 1.0, 2.0],
                [1.0, 0.0, 1.0],
                [2.0, 1.0, 0.0],
                [3.0, 2.0, 1.0],
            ]
        ),
        np.array([0, 1, 2]),
    ),
    (
        np.array(
            [
                [0.0, 1.0],
                [1.0, 0.0],
                [2.0, 1.0],
                [3.0, 2.0],
            ]
        ),
        np.array([0, 1, 2]),
    ),
    (
        np.array(
            [
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                [90, 91, 92, 93, 94, 95, 96, 97, 98, 99],
            ]
        ),
        np.array([9, 9, 9, 9, 9, 9, 9, 9, 9, 9])
    ),
    (
        np.array(
            [
                [-50, -49, -48, -47, -46, -45, -44, -43, -42, -41],
                [-10, -9, -8, -7, -6, -5, -4, -3, -2, -1],
                [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                [40, 41, 42, 43, 44, 45, 46, 47, 48, 49],
            ]
        ),
        np.array([0, 1, 8, 8, 8, 8, 8, 8, 8, 8]),
    ),
    (
        np.array([[-2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2]]),
        np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]),
    ),
    (np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]]), np.array([0, 0, 0])),
    (np.array([[0.5, 0.6, 3], [1.3, 2, -1], [-2, 0, 33], [0, 0, 0], [4, 6, -2], [-2, -1, 3]]), np.array([0, 0, 0, 2, 2]))
]
