import WordMetrics
import numpy as np
from string import punctuation
from dtwalign import dtw_from_distance_matrix
import time
from typing import List, Tuple
#from ortools.sat.python import cp_model

offset_blank = 1
TIME_THRESHOLD_MAPPING = 5.0


def get_word_distance_matrix(words_estimated: list, words_real: list) -> np.ndarray:
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
    except:
        return []


def get_resulting_string(mapped_indices: np.ndarray, words_estimated: list, words_real: list) -> Tuple[List,List]:
    mapped_words = []
    mapped_words_indices = []
    WORD_NOT_FOUND_TOKEN = '-'
    number_of_real_words = len(words_real)
    for word_idx in range(number_of_real_words):
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
            for single_word_idx in position_of_real_word_indices:
                idx_above_word = single_word_idx >= len(words_estimated)
                if idx_above_word:
                    continue
                error_word = WordMetrics.edit_distance_python(
                    words_estimated[single_word_idx], words_real[word_idx])
                if error_word < error:
                    error = error_word*1
                    best_possible_combination = words_estimated[single_word_idx]
                    best_possible_idx = single_word_idx

            mapped_words.append(best_possible_combination)
            mapped_words_indices.append(best_possible_idx)
            continue

    return mapped_words, mapped_words_indices


def get_best_mapped_words(words_estimated: list, words_real: list,use_dtw:bool = True) -> list:

    word_distance_matrix = get_word_distance_matrix(
        words_estimated, words_real)

    start = time.time()
    
    if use_dtw:
        alignment = (dtw_from_distance_matrix(
                word_distance_matrix.T))
            
        mapped_indices = alignment.get_warping_path()[:len(words_estimated)]
        duration_of_mapping = time.time()-start
    else:
        mapped_indices = get_best_path_from_distance_matrix(word_distance_matrix)

        duration_of_mapping = time.time()-start
        # In case or-tools doesn't converge, go to a faster, low-quality solution
        if len(mapped_indices) == 0 or duration_of_mapping > TIME_THRESHOLD_MAPPING+0.5:
            #mapped_indices = (dtw_from_distance_matrix(
            #    word_distance_matrix)).path[:len(words_estimated), 1]
            alignment = (dtw_from_distance_matrix(
                word_distance_matrix.T))
            
            mapped_indices = alignment.get_warping_path()

    mapped_words, mapped_words_indices = get_resulting_string(
        mapped_indices, words_estimated, words_real)

    return mapped_words, mapped_words_indices


# Faster, but not optimal
def get_best_mapped_words_dtw(words_estimated: list, words_real: list) -> list:

    from dtwalign import dtw_from_distance_matrix
    word_distance_matrix = get_word_distance_matrix(
        words_estimated, words_real)
    mapped_indices = dtw_from_distance_matrix(
        word_distance_matrix).path[:-1, 0]

    mapped_words, mapped_words_indices = get_resulting_string(
        mapped_indices, words_estimated, words_real)
    return mapped_words, mapped_words_indices


def getWhichLettersWereTranscribedCorrectly(real_word, transcribed_word):
    is_leter_correct = [None]*len(real_word)    
    for idx, letter in enumerate(real_word):   
        letter = letter.lower()    
        transcribed_word[idx] = transcribed_word[idx].lower() 
        if letter == transcribed_word[idx] or letter in punctuation:
            is_leter_correct[idx] = 1
        else:
            is_leter_correct[idx] = 0
    return is_leter_correct


def parseLetterErrorsToHTML(word_real, is_leter_correct):
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
