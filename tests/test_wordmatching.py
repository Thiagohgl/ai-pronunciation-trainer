import os
import platform
import unittest
import numpy as np
## permit to import from parent directory also in
import sys
from pathlib import Path
parent = Path(__file__).parent.parent
sys.path.append(str(parent))
import WordMatching
from constants import app_logger
from tests import set_seed
from tests import constants_wordmatching as const


class TestWordMatching(unittest.TestCase):
    def setUp(self):
        if platform.system() == "Windows" or platform.system() == "Win32":
            os.environ["PYTHONUTF8"] = "1"
            os.environ["IS_TESTING"] = "TRUE"

    def tearDown(self):
        if platform.system() == "Windows" or platform.system() == "Win32" and "PYTHONUTF8" in os.environ:
            del os.environ["PYTHONUTF8"]
            del os.environ["IS_TESTING"]

    def test_get_word_distance_matrix(self):
        words_estimated = ["hello", "world"]
        words_real = ["hello", "word"]
        expected_matrix = np.array([[0., 5.], [4., 1.], [5., 4.]])
        result_matrix = WordMatching.get_word_distance_matrix(words_estimated, words_real)
        np.testing.assert_array_equal(result_matrix, expected_matrix)

    def test_get_best_path_from_distance_matrix(self):
        for word_distance_matrix, expected_result_indices in const.get_best_path_from_distance_matrix_constants:
            set_seed()
            result_indices = WordMatching.get_best_path_from_distance_matrix(word_distance_matrix)
            np.testing.assert_array_equal(result_indices, expected_result_indices)

    def test_get_best_path_from_distance_matrix_with_inf_values(self):
        set_seed()
        try:   
            word_distance_matrix = np.array([[np.inf, 1, 2]])
            result_indices = WordMatching.get_best_path_from_distance_matrix(word_distance_matrix)
            app_logger.info(f"result_indices0: {result_indices}, {result_indices.shape} .")
            self.assertIsInstance(result_indices, np.ndarray)
            self.assertEqual(result_indices.shape, (3,))
            self.assertGreater(result_indices[0], 0)
            self.assertGreater(result_indices[1], 0)
            self.assertEqual(result_indices[2], 0)

            word_distance_matrix = np.array([[-1, np.inf, 3]])
            result_indices = WordMatching.get_best_path_from_distance_matrix(word_distance_matrix)
            app_logger.info(f"result_indices1: {result_indices}, {result_indices.shape} .")
            self.assertLess(result_indices[0], 0)
            self.assertGreater(result_indices[1], 0)
            self.assertEqual(result_indices[2], 0)
        
            word_distance_matrix = np.array([[2, -1, np.inf]])
            result_indices = WordMatching.get_best_path_from_distance_matrix(word_distance_matrix)
            app_logger.info(f"result_indices2: {result_indices}, {result_indices.shape} .")
            self.assertGreater(result_indices[0], 0)
            self.assertGreater(result_indices[1], -1)
            self.assertEqual(result_indices[2], 0)
            
            word_distance_matrix = np.array([[np.inf, 1, 2], [1, np.inf, 3], [2, 3, np.inf], [-1, -np.inf, 1]])
            result_indices = WordMatching.get_best_path_from_distance_matrix(word_distance_matrix)
            app_logger.info(f"result_indices3: {result_indices}, {result_indices.shape} .")
            self.assertGreater(result_indices[0], 0)
            self.assertGreater(result_indices[1], 0)
            self.assertEqual(result_indices[2], 0)

        except AssertionError as ae:
            app_logger.error("ae:")
            app_logger.error(ae)
            raise ae

    def test_getWhichLettersWereTranscribedCorrectly(self):
        real_word = "hello"
        transcribed_word = [x for x in "hxllo"]
        expected_result = [1, 0, 1, 1, 1]
        result = WordMatching.getWhichLettersWereTranscribedCorrectly(real_word, transcribed_word)
        self.assertEqual(result, expected_result)

    def test_get_best_mapped_words_false(self):
        words_estimated = ["hello", "world"]
        words_real = ["hello", "word"]
        expected_words = ["hello", "world"]
        expected_indices = [0, 1]
        result_words, result_indices = WordMatching.get_best_mapped_words(words_estimated, words_real, use_dtw=False)
        self.assertEqual(result_words, expected_words)
        self.assertEqual(result_indices, expected_indices)

        expected_mapped_letters = ['e', 's', 's', 'e', 'n', '-']
        expected_mapped_words_indices = [np.int64(0), np.int64(1), np.int64(2), np.int64(3), np.int64(4), -1]
        output_mapped_letters, output_mapped_words_indices = WordMatching.get_best_mapped_words("essen", "essen?", use_dtw=False)
        assert output_mapped_letters == expected_mapped_letters
        assert output_mapped_words_indices == expected_mapped_words_indices

    def test_get_word_distance_matrix_with_empty_lists(self):
        words_estimated = []
        words_real = []
        expected_matrix = np.arange(0).reshape((1, 0))
        result_matrix = WordMatching.get_word_distance_matrix(words_estimated, words_real)
        np.testing.assert_array_equal(result_matrix, expected_matrix)

    def test_get_word_distance_matrix_with_different_lengths(self):
        words_estimated = ["hello"]
        words_real = ["hello", "world"]
        expected_matrix = np.array([[0., 4.], [5., 5.]])
        result_matrix = WordMatching.get_word_distance_matrix(words_estimated, words_real)
        np.testing.assert_array_equal(result_matrix, expected_matrix)

    def test_get_best_path_from_distance_matrix_with_empty_matrix_indexerror(self):
        word_distance_matrix = np.array([])
        with self.assertRaises(IndexError):
            try:
                WordMatching.get_best_path_from_distance_matrix(word_distance_matrix)
            except IndexError as e:
                msg = "tuple index out of range"
                assert msg in str(e)
                raise e

    def test_getWhichLettersWereTranscribedCorrectly_with_empty_strings(self):
        real_word = ""
        transcribed_word = [""]
        expected_result = []
        result = WordMatching.getWhichLettersWereTranscribedCorrectly(real_word, transcribed_word)
        self.assertEqual(result, expected_result)

    def test_getWhichLettersWereTranscribedCorrectly_with_different_lengths(self):
        real_word = "hello"
        transcribed_word = [x for x in "hello oo"]
        expected_result = [1, 1, 1, 1, 1]
        result = WordMatching.getWhichLettersWereTranscribedCorrectly(real_word, transcribed_word)
        self.assertEqual(result, expected_result)

    def test_getWhichLettersWereTranscribedCorrectly_wrong_number_elements_mapped_letters(self):
        word_real = "ich"
        mapped_letters=['i', 'c', 'h', "z"]
        is_letter_correct1 = WordMatching.getWhichLettersWereTranscribedCorrectly(word_real, mapped_letters)  # , mapped_letters_indices)
        self.assertEqual(is_letter_correct1, [1, 1, 1])
        
    def test_getWhichLettersWereTranscribedCorrectly_wrong_number_elements_mapped_letters(self):
        word_real = "ichh"
        mapped_letters=['i', 'c', 'h']
        with self.assertRaises(IndexError):
            try:
                WordMatching.getWhichLettersWereTranscribedCorrectly(word_real, mapped_letters)  # , mapped_letters_indices)
            except IndexError as e:
                msg = 'list index out of range'
                assert msg in str(e)
                raise e

    def test_get_best_mapped_words_with_empty_lists_false(self):
        expected_words = ["?"]
        expected_indices = [0]
        result_words, result_indices = WordMatching.get_best_mapped_words("?", "-", use_dtw=False)
        self.assertEqual(result_words, expected_words)
        self.assertEqual(result_indices, expected_indices)
        expected_words = ['b', 'i', 'n', '-']
        expected_indices = [np.int64(0), np.int64(1), np.int64(2), -1]
        result_words, result_indices = WordMatching.get_best_mapped_words("bin", "bind", use_dtw=False)
        self.assertEqual(result_words, expected_words)
        self.assertEqual(result_indices, expected_indices)

    def test_get_best_mapped_words_with_different_lengths_false(self):
        result_words, result_indices = WordMatching.get_best_mapped_words("bin", "", use_dtw=False)
        self.assertEqual(result_words, [])
        self.assertEqual(result_indices, [])

    def test_get_best_mapped_words_with_word_estimated_empty_real_word_not_empty_false(self):
        result_words, result_indices = WordMatching.get_best_mapped_words("", "bin", use_dtw=False)
        self.assertEqual(result_words, ['', '-', '-'])
        self.assertEqual(result_indices, [-1, -1, -1])

    def test_get_best_mapped_words_with_word_estimated_real_word_both_empty_false(self):
        try:
            with self.assertRaises(IndexError):
                try:
                    WordMatching.get_best_mapped_words("", "", use_dtw=False)
                except IndexError as ie:
                    app_logger.error(f"raised IndexError, ie.args: {ie.args} => exception: {ie} ##")
                    msg = "index -1 is out of bounds for axis {axis} with size 0"
                    assert msg.format(axis=0) in str(ie) or msg.format(axis=1) in str(ie)
                    raise ie
        except AssertionError:
            # for some reason executing the test in debug mode from Visual Studio Code raises an AssertionError instead of an IndexError
            app_logger.error("raised AssertionError instead than IndexError...")
            with self.assertRaises(AssertionError):
                try:
                    WordMatching.get_best_mapped_words("", "", use_dtw=False)
                except AssertionError as ae:
                    msg = "code object dtw_low at "
                    assert msg in str(ae)
                    raise ae

    def test_get_best_mapped_words_survived_false(self):
        set_seed()

        word_real = "habe"
        for word_estimated, expected_letters, expected_indices in [
            ("habe", ["h", "a", "b", "e"], [0, 1, 2, 3]),
            ("hobe", ["h", "-", "b", "e"], [0, -1, 2, 3]),
            ("hone", ["h", "-", "-", "e"], [0, -1, -1, 3]),
            ("honi", ["h", "-", "-", "-"], [0, -1, -1, -1]),
            ("koni", ["k", "-", "-", "-"], [0, -1, -1, -1]),
            ("kabe", ["k", "a", "b", "e"], [0, 1, 2, 3]),
            ("kane", ["k", "a", "-", "e"], [0, 1, -1, 3]),
        ]:
            result_words, result_indices = WordMatching.get_best_mapped_words(word_estimated, word_real, use_dtw=False)
            try:
                self.assertEqual(result_words, expected_letters)
                self.assertEqual(result_indices, expected_indices)
            except AssertionError as ae:
                app_logger.error("ae:", ae, "#", word_estimated, "#", word_real, "#", expected_letters, "#", expected_indices, "##")
                raise ae

    def test_get_resulting_string1(self):
        set_seed()
        mapped_indices = np.array([0, 1])
        words_estimated = ["hello", "world"]
        words_real = ["hello", "word"]
        expected_words = ["hello", "world"]
        expected_indices = [0, 1]
        result_words, result_indices = WordMatching.get_resulting_string(mapped_indices, words_estimated, words_real)
        self.assertEqual(result_words, expected_words)
        self.assertEqual(result_indices, expected_indices)

    def test_get_resulting_string2(self):
        set_seed()
        mapped_indices = np.array([0, 1])
        words_estimated = ["hollo", "uorld"]
        words_real = ["hello", "word"]
        expected_words = ['hollo', 'uorld']
        expected_indices = [0, 1]
        result_words, result_indices = WordMatching.get_resulting_string(mapped_indices, words_estimated, words_real)
        self.assertEqual(result_words, expected_words)
        self.assertEqual(result_indices, expected_indices)

        mapped_indices = np.array([1, 1])
        expected_words = ['-', 'uorld']
        expected_indices = [-1, 1]
        result_words, result_indices = WordMatching.get_resulting_string(mapped_indices, words_estimated, words_real)
        self.assertEqual(result_words, expected_words)
        self.assertEqual(result_indices, expected_indices)

        mapped_indices = np.array([0, 0])
        expected_words = ['hollo', '-']
        expected_indices = [0, -1]
        result_words, result_indices = WordMatching.get_resulting_string(mapped_indices, words_estimated, words_real)
        self.assertEqual(result_words, expected_words)
        self.assertEqual(result_indices, expected_indices)

        mapped_indices = np.array([0, -1])
        expected_words = ["hollo", "-"]
        expected_indices = [0, -1]
        result_words, result_indices = WordMatching.get_resulting_string(mapped_indices, words_estimated, words_real)
        self.assertEqual(result_words, expected_words)
        self.assertEqual(result_indices, expected_indices)
        
        mapped_indices = np.array([-1, -1])
        expected_words = ["-", "-"]
        expected_indices = [-1, -1]
        result_words, result_indices = WordMatching.get_resulting_string(mapped_indices, words_estimated, words_real)
        self.assertEqual(result_words, expected_words)
        self.assertEqual(result_indices, expected_indices)

    def test_get_resulting_string_with_empty_lists(self):
        mapped_indices = np.array([])
        words_estimated = []
        words_real = []
        expected_words = []
        expected_indices = []
        result_words, result_indices = WordMatching.get_resulting_string(mapped_indices, words_estimated, words_real)
        self.assertEqual(result_words, expected_words)
        self.assertEqual(result_indices, expected_indices)


if __name__ == '__main__':
    unittest.main()
