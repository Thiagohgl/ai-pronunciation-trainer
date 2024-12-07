import time
from string import punctuation

import numpy as np
from dtwalign import dtw_from_distance_matrix
from ortools.sat.python import cp_model

from . import WordMetrics, app_logger

offset_blank = 1
TIME_THRESHOLD_MAPPING = 5.0


def get_word_distance_matrix(words_estimated: list, words_real: list) -> np.array:
    """
    Computes a distance matrix between estimated words and real words using edit distance.

    Args:
        words_estimated (list): A list of estimated words.
        words_real (list): A list of real words.

    Returns:
        np.array: A 2D numpy array where each element [i, j] represents the edit distance
                  between words_estimated[i] and words_real[j]. If offset_blank is 1, an
                  additional row is added to the matrix representing the length of each
                  real word.
    """
    number_of_real_words = len(words_real)
    number_of_estimated_words = len(words_estimated)

    word_distance_matrix = np.zeros(
        (number_of_estimated_words+offset_blank, number_of_real_words))
    for idx_estimated in range(number_of_estimated_words):
        for idx_real in range(number_of_real_words):
            word_distance_matrix[idx_estimated, idx_real] = WordMetrics.edit_distance_python(
                words_estimated[idx_estimated], words_real[idx_real])

    if offset_blank == 1:
        for idx_real in range(number_of_real_words):
            word_distance_matrix[number_of_estimated_words,
                                 idx_real] = len(words_real[idx_real])
    return word_distance_matrix


def get_best_path_from_distance_matrix(word_distance_matrix):
    """
    Finds the best path from a distance matrix using constraint programming.

    This function takes a word distance matrix and uses the Google OR-Tools
    constraint programming solver to find the optimal mapping of estimated words
    to real words that minimizes the total phoneme distance.

    Args:
        word_distance_matrix (np.ndarray): A 2D numpy array where each element
                                           represents the distance between an
                                           estimated word and a real word.

    Returns:
        np.ndarray: An array of indices representing the best mapping of
                    estimated words to real words. If an error occurs, an empty
                    list is returned.
    """
    modelCpp = cp_model.CpModel()

    number_of_real_words = word_distance_matrix.shape[1]
    number_of_estimated_words = word_distance_matrix.shape[0]-1

    number_words = np.maximum(number_of_real_words, number_of_estimated_words)

    estimated_words_order = [modelCpp.NewIntVar(0, int(
        number_words - 1 + offset_blank), 'w%i' % i) for i in range(number_words+offset_blank)]

    # They are in ascending order
    for word_idx in range(number_words-1):
        modelCpp.Add(
            estimated_words_order[word_idx+1] >= estimated_words_order[word_idx])

    total_phoneme_distance = 0
    real_word_at_time = {}
    for idx_estimated in range(number_of_estimated_words):
        for idx_real in range(number_of_real_words):
            real_word_at_time[idx_estimated, idx_real] = modelCpp.NewBoolVar(
                'real_word_at_time'+str(idx_real)+'-'+str(idx_estimated))
            modelCpp.Add(estimated_words_order[idx_estimated] == idx_real).OnlyEnforceIf(
                real_word_at_time[idx_estimated, idx_real])
            total_phoneme_distance += word_distance_matrix[idx_estimated,
                                                           idx_real]*real_word_at_time[idx_estimated, idx_real]

    # If no word in time, difference is calculated from empty string
    for idx_real in range(number_of_real_words):
        word_has_a_match = modelCpp.NewBoolVar(
            'word_has_a_match'+str(idx_real))
        modelCpp.Add(sum([real_word_at_time[idx_estimated, idx_real] for idx_estimated in range(
            number_of_estimated_words)]) == 1).OnlyEnforceIf(word_has_a_match)
        total_phoneme_distance += word_distance_matrix[number_of_estimated_words,
                                                       idx_real]*word_has_a_match.Not()

    # Loss should be minimized
    modelCpp.Minimize(total_phoneme_distance)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = TIME_THRESHOLD_MAPPING
    status = solver.Solve(modelCpp)

    mapped_indices = []
    try:
        for word_idx in range(number_words):
            mapped_indices.append(
                (solver.Value(estimated_words_order[word_idx])))

        return np.array(mapped_indices, dtype=int)
    except Exception as ex:
        app_logger.error(f"ex:{ex}.")
        return []


def get_resulting_string(mapped_indices: np.array, words_estimated: list, words_real: list) -> tuple[list, list]:
    """
    Maps the indices of real words to the estimated words and returns the resulting mapped words and their indices.

    Args:
        mapped_indices (np.array): An array of indices mapping real words to estimated words.
        words_estimated (list): A list of estimated words.
        words_real (list): A list of real words.

    Returns:
        tuple[list, list]: A tuple containing two lists:
            - mapped_words (list): A list of words where each word is either an estimated word or a placeholder token if no match is found.
            - mapped_words_indices (list): A list of indices corresponding to the positions of the mapped words in the estimated words list.
    """
    mapped_words = []
    mapped_words_indices = []
    WORD_NOT_FOUND_TOKEN = '-'
    number_of_real_words = len(words_real)
    for word_idx in range(number_of_real_words):
        app_logger.debug(f"{word_idx} => {mapped_indices} == {word_idx}, {mapped_indices == word_idx} #")
        position_of_real_word_indices = np.where(
            mapped_indices == word_idx)[0].astype(int)

        if len(position_of_real_word_indices) == 0:
            mapped_words.append(WORD_NOT_FOUND_TOKEN)
            mapped_words_indices.append(-1)
            continue

        if len(position_of_real_word_indices) == 1:
            mapped_words.append(
                words_estimated[position_of_real_word_indices[0]])
            mapped_words_indices.append(position_of_real_word_indices[0])
            continue
        # Check which index gives the lowest error
        if len(position_of_real_word_indices) > 1:
            error = 99999
            best_possible_combination = ''
            best_possible_idx = -1
            best_possible_combination, best_possible_idx = inner_get_resulting_string(
                best_possible_combination, best_possible_idx, error, position_of_real_word_indices,
                word_idx, words_estimated, words_real
            )

            mapped_words.append(best_possible_combination)
            mapped_words_indices.append(best_possible_idx)
            # continue

    return mapped_words, mapped_words_indices


def inner_get_resulting_string(
        best_possible_combination, best_possible_idx, error, position_of_real_word_indices, word_idx, words_estimated, words_real
    ):
    """
    Determines the best possible word combination and its index based on the minimum edit distance error.

    Args:
        best_possible_combination (str): The current best possible word combination.
        best_possible_idx (int): The index of the current best possible word combination.
        error (float): The current minimum edit distance error.
        position_of_real_word_indices (list): List of indices representing positions of real words.
        word_idx (int): The index of the real word being compared.
        words_estimated (list): List of estimated words.
        words_real (list): List of real words.

    Returns:
        tuple: A tuple containing the best possible word combination (str) and its index (int).
    """
    for single_word_idx in position_of_real_word_indices:
        idx_above_word = single_word_idx >= len(words_estimated)
        if idx_above_word:
            continue
        error_word = WordMetrics.edit_distance_python(
            words_estimated[single_word_idx], words_real[word_idx])
        if error_word < error:
            error = error_word * 1
            best_possible_combination = words_estimated[single_word_idx]
            best_possible_idx = single_word_idx
    return best_possible_combination, best_possible_idx


def get_best_mapped_words(words_estimated: list, words_real: list) -> tuple[list, list]:
    """
    Maps the estimated words to the real words based on a distance matrix and returns the best-matched words and their indices.

    Args:
        words_estimated (list): A list of estimated words.
        words_real (list): A list of real words.

    Returns:
        tuple[list, list]: A tuple containing two lists:
            - mapped_words: A list of words that are the best match from the estimated words to the real words.
            - mapped_words_indices: A list of indices representing the mapping from estimated words to real words.
    """

    word_distance_matrix = get_word_distance_matrix(
        words_estimated, words_real)

    start = time.time()
    mapped_indices = get_best_path_from_distance_matrix(word_distance_matrix)

    duration_of_mapping = time.time()-start
    # In case or-tools doesn't converge, go to a faster, low-quality solution
    if len(mapped_indices) == 0 or duration_of_mapping > TIME_THRESHOLD_MAPPING+0.5:
        mapped_indices = (dtw_from_distance_matrix(
            word_distance_matrix)).path[:len(words_estimated), 1]

    mapped_words, mapped_words_indices = get_resulting_string(
        mapped_indices, words_estimated, words_real)

    return mapped_words, mapped_words_indices


def get_best_mapped_words_dtw(words_estimated: list, words_real: list) -> list:
    """
    Computes a mapped words between the estimated words and the real words using Dynamic Time Warping (DTW).
    Faster, but not optimal.

    Args:
        words_estimated (list): A list of estimated words.
        words_real (list): A list of real words.

    Returns:
        list: A list containing the mapped words and their corresponding indices.
    """

    from dtwalign import dtw_from_distance_matrix
    word_distance_matrix = get_word_distance_matrix(
        words_estimated, words_real)
    mapped_indices = dtw_from_distance_matrix(
        word_distance_matrix).path[:-1, 0]

    mapped_words, mapped_words_indices = get_resulting_string(
        mapped_indices, words_estimated, words_real)
    return mapped_words, mapped_words_indices


def getWhichLettersWereTranscribedCorrectly(real_word, transcribed_word):
    """
    Compares each letter of the real word with the corresponding letter in the transcribed word
    and determines if they match.

    Args:
        real_word (str): The original word.
        transcribed_word (str): The word as transcribed.

    Returns:
        list: A list of integers where 1 indicates the letter was correctly transcribed,
              0 indicates it was incorrectly transcribed, and None indicates no comparison was made.
    """
    is_leter_correct = [None]*len(real_word)
    for idx, letter in enumerate(real_word):
        if letter == transcribed_word[idx] or letter in punctuation:
            is_leter_correct[idx] = 1
        else:
            is_leter_correct[idx] = 0
    return is_leter_correct


def parseLetterErrorsToHTML(word_real, is_leter_correct):
    """
    Converts a word into a colored HTML-like string based on letter correctness.

    Args:
        word_real (str): The original word to be processed.
        is_leter_correct (list of int): A list indicating the correctness of each letter in the word.
                                        A value of 1 means the letter is correct, and 0 means it is incorrect.

    Returns:
        str: The word with letters wrapped in markers indicating correctness.
             Correct letters are wrapped with '*' and incorrect letters are wrapped with '-'.
    """
    word_colored = ''
    correct_color_start = '*'
    correct_color_end = '*'
    wrong_color_start = '-'
    wrong_color_end = '-'
    for idx, letter in enumerate(word_real):
        if is_leter_correct[idx] == 1:
            word_colored += correct_color_start + letter+correct_color_end
        else:
            word_colored += wrong_color_start + letter+wrong_color_end
    return word_colored
