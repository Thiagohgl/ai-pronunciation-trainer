import unittest

import numpy as np
import torch
from torchaudio.transforms import Resample
## permit to import from parent directory also in
# import sys
# from pathlib import Path
# parent = Path(__file__).parent.parent
# sys.path.append(str(parent))
from lambdaSpeechToScore import audioread_load
import pronunciationTrainer
from constants import sample_rate_start, sample_rate_resample

from tests import EVENTS_FOLDER, set_seed
import tests.utilities as utilities


phrases = {
    "de": {
        "real": "Hallo, wie geht es dir?",
        "transcribed": ' Hallo, wie geht es dir?',
        "partial": 'hallo wie geht ',
        "incorrect": 'hail wi git es dir'
    },
    "en": {
        "real": "Hi there, how are you?",
        "transcribed": ' Hi there, how are you?',
        "partial": 'i there how',
        "incorrect": "I here how re youth"
    }
}
trainer_SST_lambda_de = pronunciationTrainer.getTrainer("de")
trainer_SST_lambda_en = pronunciationTrainer.getTrainer("en")
signal_de, samplerate = audioread_load(str(EVENTS_FOLDER / "test_de_easy.wav"))
signal_en, samplerate = audioread_load(str(EVENTS_FOLDER / "test_en_easy.wav"))
transform = Resample(orig_freq=sample_rate_start, new_freq=sample_rate_resample)


class TestScore(unittest.TestCase):
    def setUp(self):
        import platform, os
        if platform.system() == "Windows" or platform.system() == "Win32":
            os.environ["PYTHONUTF8"] = "1"

    def test_getTrainer(self):
        self.assertIsInstance(trainer_SST_lambda_de, pronunciationTrainer.PronunciationTrainer)
        self.assertIsInstance(trainer_SST_lambda_en, pronunciationTrainer.PronunciationTrainer)

    def test_exact_transcription_de(self):
        set_seed()
        phrase_real = phrases["de"]["real"]
        real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = trainer_SST_lambda_de.matchSampleAndRecordedWords(phrase_real, phrase_real)
        self.assertEqual(real_and_transcribed_words_ipa, [('haloː,', 'haloː,'), ('viː', 'viː'), ('ɡeːt', 'ɡeːt'), ('ɛːs', 'ɛːs'), ('diːr?', 'diːr?')])
        self.assertEqual(mapped_words_indices, [0, 1, 2, 3, 4])
        pronunciation_accuracy, current_words_pronunciation_accuracy = trainer_SST_lambda_de.getPronunciationAccuracy(real_and_transcribed_words)
        self.assertEqual(int(pronunciation_accuracy), 100)
        self.assertEqual(current_words_pronunciation_accuracy, [100, 100, 100, 100, 100])

    def test_transcription_de(self):
        set_seed()
        phrase_real = phrases["de"]["real"]
        phrase_transcribed = phrases["de"]["transcribed"]
        real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = trainer_SST_lambda_de.matchSampleAndRecordedWords(phrase_real, phrase_transcribed)
        self.assertEqual(real_and_transcribed_words_ipa, [('haloː,', 'haloː,'), ('viː', 'viː'), ('ɡeːt', 'ɡeːt'), ('ɛːs', 'ɛːs'), ('diːr?', 'diːr?')])
        self.assertEqual(mapped_words_indices, [0, 1, 2, 3, 4])
        pronunciation_accuracy, current_words_pronunciation_accuracy= trainer_SST_lambda_de.getPronunciationAccuracy(real_and_transcribed_words)
        self.assertEqual(int(pronunciation_accuracy), 100)
        self.assertEqual(current_words_pronunciation_accuracy, [100, 100, 100, 100, 100])

    def test_partial_transcription_de(self):
        set_seed()
        self.maxDiff = None
        phrase_real = phrases["de"]["real"]
        phrase_partial = phrases["de"]["partial"]
        real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = trainer_SST_lambda_de.matchSampleAndRecordedWords(phrase_real, phrase_partial)
        pronunciation_accuracy, current_words_pronunciation_accuracy= trainer_SST_lambda_de.getPronunciationAccuracy(real_and_transcribed_words)
        self.assertEqual(real_and_transcribed_words_ipa, [('haloː,', 'haloː'), ('viː', 'viː'), ('ɡeːt', 'ɡeːt'), ('ɛːs', '-'), ('diːr?', '-')] )
        self.assertEqual(mapped_words_indices, [0, 1, 2, -1, -1])
        self.assertEqual(int(pronunciation_accuracy), 71)
        self.assertEqual(current_words_pronunciation_accuracy, [100.0, 100.0, 100.0, 0.0, 0.0])

    def test_incorrect_transcription_with_correct_words_de(self):
        set_seed()
        phrase_real = phrases["de"]["real"]
        phrase_transcribed_incorrect = phrases["de"]["incorrect"]
        real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = trainer_SST_lambda_de.matchSampleAndRecordedWords(phrase_real, phrase_transcribed_incorrect)
        self.assertEqual(real_and_transcribed_words_ipa, [('haloː,', 'haɪ̯l'), ('viː', 'viː'), ('ɡeːt', 'ɡiːt'), ('ɛːs', 'ɛːs'), ('diːr?', 'diːɐ̯')])
        self.assertEqual(mapped_words_indices, [0, 1, 2, 3, 4])
        pronunciation_accuracy, current_words_pronunciation_accuracy= trainer_SST_lambda_de.getPronunciationAccuracy(real_and_transcribed_words)
        self.assertEqual(int(pronunciation_accuracy), 71)
        for accuracy, expected_accuracy in zip(current_words_pronunciation_accuracy, [60.0, 66.666666, 50.0, 100.0, 100.0]):
            self.assertAlmostEqual(accuracy, expected_accuracy, places=2)

    def test_exact_transcription_en(self):
        set_seed()
        phrase_real = phrases["en"]["real"]
        real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = trainer_SST_lambda_en.matchSampleAndRecordedWords(phrase_real, phrase_real)
        self.assertEqual(real_and_transcribed_words_ipa, [('haɪ', 'haɪ'), ('ðɛr,', 'ðɛr,'), ('haʊ', 'haʊ'), ('ər', 'ər'), ('ju?', 'ju?')])
        self.assertEqual(mapped_words_indices, [0, 1, 2, 3, 4])
        pronunciation_accuracy, current_words_pronunciation_accuracy= trainer_SST_lambda_en.getPronunciationAccuracy(real_and_transcribed_words)
        self.assertEqual(int(pronunciation_accuracy), 100)
        self.assertEqual(current_words_pronunciation_accuracy, [100, 100, 100, 100, 100])

    def test_transcription_en(self):
        set_seed()
        phrase_real = phrases["en"]["real"]
        phrase_transcribed = phrases["en"]["transcribed"]
        real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = trainer_SST_lambda_en.matchSampleAndRecordedWords(phrase_real, phrase_transcribed)
        self.assertEqual(real_and_transcribed_words_ipa, [('haɪ', 'haɪ'), ('ðɛr,', 'ðɛr,'), ('haʊ', 'haʊ'), ('ər', 'ər'), ('ju?', 'ju?')])
        self.assertEqual(mapped_words_indices, [0, 1, 2, 3, 4])
        pronunciation_accuracy, current_words_pronunciation_accuracy= trainer_SST_lambda_en.getPronunciationAccuracy(real_and_transcribed_words)
        self.assertEqual(int(pronunciation_accuracy), 100)
        self.assertEqual(current_words_pronunciation_accuracy, [100.0, 100.0, 100.0, 100.0, 100.0])

    def test_partial_transcription_en(self):
        set_seed()
        self.maxDiff = None
        phrase_real = phrases["en"]["real"]
        phrase_partial = phrases["en"]["partial"]
        real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = trainer_SST_lambda_en.matchSampleAndRecordedWords(phrase_real, phrase_partial)
        self.assertEqual(real_and_transcribed_words_ipa, [('haɪ', 'aɪ'), ('ðɛr,', 'ðɛr'), ('haʊ', 'haʊ'), ('ər', ''), ('ju?', '')])
        self.assertEqual(mapped_words_indices, [0, 1, 2, -1, -1])
        pronunciation_accuracy, current_words_pronunciation_accuracy= trainer_SST_lambda_en.getPronunciationAccuracy(real_and_transcribed_words)
        self.assertEqual(int(pronunciation_accuracy), 56)
        self.assertEqual(current_words_pronunciation_accuracy, [50.0, 100.0, 100.0, 0.0, 0.0])

    def test_incorrect_transcription_with_correct_words_en(self):
        set_seed()
        phrase_real = phrases["en"]["real"]
        phrase_transcribed_incorrect = phrases["en"]["incorrect"]
        real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = trainer_SST_lambda_en.matchSampleAndRecordedWords(phrase_real, phrase_transcribed_incorrect)
        self.assertEqual(real_and_transcribed_words_ipa, [('haɪ', 'aɪ'), ('ðɛr,', 'hir'), ('haʊ', 'haʊ'), ('ər', 'ri'), ('ju?', 'juθ')])
        self.assertEqual(mapped_words_indices, [0, 1, 2, 3, 4])
        pronunciation_accuracy, current_words_pronunciation_accuracy= trainer_SST_lambda_en.getPronunciationAccuracy(real_and_transcribed_words)
        self.assertEqual(int(pronunciation_accuracy), 69)
        for accuracy, expected_accuracy in zip(current_words_pronunciation_accuracy, [50.0, 80.0, 100.0, 66.666666, 33.333333]):
            self.assertAlmostEqual(accuracy, expected_accuracy, places=2)

    def test_processAudioForGivenText_getTranscriptAndWordsLocations_de(self):
        set_seed()
        self.maxDiff = None
        phrase_real = phrases["de"]["real"]
        signal_de_shape = signal_de.shape[0]
        signal_transformed = transform(torch.Tensor(signal_de)).unsqueeze(0)
        result = trainer_SST_lambda_de.processAudioForGivenText(signal_transformed, phrase_real)
        expected_result = {
            'recording_transcript': ' Hallo, wie geht es dir?',
            'real_and_transcribed_words': [('Hallo,', 'Hallo,'), ('wie', 'wie'), ('geht', 'geht'), ('es', 'es'), ('dir?', 'dir?')],
            'recording_ipa': ' haloː, viː ɡeːt ɛːs diːr?',
            'start_time': '0.0 0.49 0.59 0.77 0.99',
            'end_time': '0.37 0.69 0.87 1.09 1.31',
            'real_and_transcribed_words_ipa': [('haloː,', 'haloː,'), ('viː', 'viː'), ('ɡeːt', 'ɡeːt'), ('ɛːs', 'ɛːs'), ('diːr?', 'diːr?')],
            'pronunciation_accuracy': 100.0,
            'pronunciation_categories': [0, 0, 0, 0, 0]
        }
        self.assertDictEqual(result, expected_result)
        transcript, word_locations = trainer_SST_lambda_de.getTranscriptAndWordsLocations(signal_de_shape)
        assert transcript == phrases["de"]["transcribed"]
        assert word_locations == [(0, 5920), (7840, 11040), (9440, 13920), (12320, 17440), (15840, 20960)]

    def test_processAudioForGivenText_de(self):
        set_seed()
        self.maxDiff = None
        phrase_real = phrases["de"]["real"]
        signal_transformed = transform(torch.Tensor(signal_de)).unsqueeze(0)
        expected_result = {
            'recording_transcript': ' Hallo, wie geht es dir?',
            'real_and_transcribed_words': [('Hallo,', 'Hallo,'), ('wie', 'wie'), ('geht', 'geht'), ('es', 'es'), ('dir?', 'dir?')],
            'recording_ipa': ' haloː, viː ɡeːt ɛːs diːr?',
            'start_time': '0.0 0.49 0.59 0.77 0.99',
            'end_time': '0.37 0.69 0.87 1.09 1.31',
            'real_and_transcribed_words_ipa': [('haloː,', 'haloː,'), ('viː', 'viː'), ('ɡeːt', 'ɡeːt'), ('ɛːs', 'ɛːs'), ('diːr?', 'diːr?')],
            'pronunciation_accuracy': 100.0,
            'pronunciation_categories': [0, 0, 0, 0, 0]
        }
        result = trainer_SST_lambda_de.processAudioForGivenText(signal_transformed, phrase_real)
        self.assertDictEqual(result, expected_result)

    def test_removePunctuation_de(self):
        word = "glück,"
        cleaned_word = trainer_SST_lambda_de.removePunctuation(word)
        self.assertEqual(cleaned_word, "glück")
        word = "glück,\n\rhallo..."
        cleaned_word = trainer_SST_lambda_de.removePunctuation(word)
        self.assertEqual(cleaned_word, "glück\n\rhallo")

    def test_getWordsPronunciationCategory_de(self):
        accuracies = [x for x in range(-121, 121, 10)] + [np.inf, -np.inf, np.nan, 1.5, -1.5]
        expected_categories = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2]
        categories = trainer_SST_lambda_de.getWordsPronunciationCategory(accuracies)
        self.assertEqual(categories, expected_categories)

    def test_preprocessAudio_de(self):
        output_hash = utilities.hash_calculate(signal_de, is_file=False)
        assert output_hash == b'D9pMFzYL1BSPPg89ZCQE61xzb7QICXolYtC9EJRpvS0='
        signal_transformed = transform(torch.Tensor(signal_de)).unsqueeze(0)
        preprocessed_audio = trainer_SST_lambda_de.preprocessAudio(signal_transformed)
        self.assertIsInstance(preprocessed_audio, torch.Tensor)
        self.assertEqual(preprocessed_audio.shape, (1, 23400))
        output_hash = utilities.hash_calculate(preprocessed_audio.numpy(), is_file=False)
        assert output_hash == b'Ri/1rmgYmRSWaAw/Y3PoLEu1woiczhSUdUCbaMf++EM='

    def test_preprocessAudioStandalone_de(self):
        output_hash = utilities.hash_calculate(signal_de, is_file=False)
        assert output_hash == b'D9pMFzYL1BSPPg89ZCQE61xzb7QICXolYtC9EJRpvS0='
        signal_transformed = transform(torch.Tensor(signal_de)).unsqueeze(0)
        preprocessed_audio = pronunciationTrainer.preprocessAudioStandalone(signal_transformed)
        self.assertIsInstance(preprocessed_audio, torch.Tensor)
        self.assertEqual(preprocessed_audio.shape, (1, 23400))
        output_hash = utilities.hash_calculate(preprocessed_audio.numpy(), is_file=False)
        assert output_hash == b'Ri/1rmgYmRSWaAw/Y3PoLEu1woiczhSUdUCbaMf++EM='

    def test_processAudioForGivenText_getTranscriptAndWordsLocations_en(self):
        set_seed()
        self.maxDiff = None
        phrase_real = phrases["en"]["real"]
        signal_en_shape = signal_en.shape[0]
        signal_transformed = transform(torch.Tensor(signal_en)).unsqueeze(0)
        result = trainer_SST_lambda_en.processAudioForGivenText(signal_transformed, phrase_real)
        expected_result = {
            'recording_transcript': ' Hi there, how are you?',
            'real_and_transcribed_words': [('Hi', 'Hi'), ('there,', 'there,'), ('how', 'how'), ('are', 'are'), ('you?', 'you?')],
            'recording_ipa': 'haɪ ðɛr, haʊ ər ju?',
            'start_time': '0.0 0.09 0.41 0.53 0.65',
            'end_time': '0.19 0.35 0.63 0.75 0.91',
            'real_and_transcribed_words_ipa': [('haɪ', 'haɪ'), ('ðɛr,', 'ðɛr,'), ('haʊ', 'haʊ'), ('ər', 'ər'), ('ju?', 'ju?')],
            'pronunciation_accuracy': 100.0,
            'pronunciation_categories': [0, 0, 0, 0, 0]
        }
        self.assertDictEqual(result, expected_result)
        transcript, word_locations = trainer_SST_lambda_en.getTranscriptAndWordsLocations(signal_en_shape)
        assert transcript == phrases["en"]["transcribed"]
        assert word_locations == [(0, 3040), (1440, 5600), (6560, 10080), (8480, 12000), (10400, 14560)]

    def test_processAudioForGivenText_en(self):
        set_seed()
        self.maxDiff = None
        phrase_real = phrases["en"]["real"]
        signal_transformed = transform(torch.Tensor(signal_en)).unsqueeze(0)
        expected_result = {
            'recording_transcript': ' Hi there, how are you?',
            'real_and_transcribed_words': [('Hi', 'Hi'), ('there,', 'there,'), ('how', 'how'), ('are', 'are'), ('you?', 'you?')],
            'recording_ipa': 'haɪ ðɛr, haʊ ər ju?',
            'start_time': '0.0 0.09 0.41 0.53 0.65',
            'end_time': '0.19 0.35 0.63 0.75 0.91',
            'real_and_transcribed_words_ipa': [('haɪ', 'haɪ'), ('ðɛr,', 'ðɛr,'), ('haʊ', 'haʊ'), ('ər', 'ər'), ('ju?', 'ju?')],
            'pronunciation_accuracy': 100.0,
            'pronunciation_categories': [0, 0, 0, 0, 0],
        }
        
        result = trainer_SST_lambda_en.processAudioForGivenText(signal_transformed, phrase_real)
        self.assertDictEqual(result, expected_result)

    def test_getPronunciationCategoryFromAccuracy_en(self):
        accuracies = [x for x in range(-121, 121, 10)] + [np.inf, -np.inf, np.nan, 1.5, -1.5]
        expected_categories = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2]
        all_categories = []
        for accuracy in accuracies:
            category = trainer_SST_lambda_en.getPronunciationCategoryFromAccuracy(accuracy)
            all_categories.append(category)
        self.assertEqual(all_categories, expected_categories)

    def test_matchSampleAndRecordedWords(self):
        set_seed()
        phrase_real = phrases["de"]["real"]
        phrase_transcribed = phrases["de"]["transcribed"]
        real_and_transcribed_words, real_words, transcribed_words = trainer_SST_lambda_de.matchSampleAndRecordedWords(phrase_real, phrase_transcribed)
        self.assertIsInstance(real_and_transcribed_words, list)
        self.assertIsInstance(real_words, list)
        self.assertIsInstance(transcribed_words, list)
        self.assertEqual(len(real_and_transcribed_words), len(real_words))
        self.assertEqual(len(real_and_transcribed_words), len(transcribed_words))

    def test_removePunctuation_en(self):
        word = "hello,"
        cleaned_word = trainer_SST_lambda_en.removePunctuation(word)
        self.assertEqual(cleaned_word, "hello")
        word = "hello,\n\rworld..."
        cleaned_word = trainer_SST_lambda_en.removePunctuation(word)
        self.assertEqual(cleaned_word, "hello\n\rworld")

    def test_getWordsPronunciationCategory_en(self):
        accuracies = [x for x in range(-121, 121, 10)] + [np.inf, -np.inf, np.nan, 1.5, -1.5]
        expected_categories = [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2]
        categories = trainer_SST_lambda_en.getWordsPronunciationCategory(accuracies)
        self.assertEqual(categories, expected_categories)

    def test_preprocessAudio_en(self):
        output_hash = utilities.hash_calculate(signal_en, is_file=False)
        assert output_hash == b'zBAV/y7mecyPHLGiitHRP9vK7oU9hnYvyuatU0PQfts='
        signal_transformed = transform(torch.Tensor(signal_en)).unsqueeze(0)
        preprocessed_audio = trainer_SST_lambda_en.preprocessAudio(signal_transformed)
        self.assertIsInstance(preprocessed_audio, torch.Tensor)
        self.assertEqual(preprocessed_audio.shape, (1, 16800))
        output_hash = utilities.hash_calculate(preprocessed_audio.numpy(), is_file=False)
        assert output_hash == b'KsyH1MXIc+5e5B6CcijhitsGPUDRJjrJU2qg8bQi600='

    def test_preprocessAudioStandalone_en(self):
        output_hash = utilities.hash_calculate(signal_en, is_file=False)
        assert output_hash == b'zBAV/y7mecyPHLGiitHRP9vK7oU9hnYvyuatU0PQfts='
        signal_transformed = transform(torch.Tensor(signal_en)).unsqueeze(0)
        preprocessed_audio = pronunciationTrainer.preprocessAudioStandalone(signal_transformed)
        self.assertIsInstance(preprocessed_audio, torch.Tensor)
        self.assertEqual(preprocessed_audio.shape, (1, 16800))
        output_hash = utilities.hash_calculate(preprocessed_audio.numpy(), is_file=False)
        assert output_hash == b'KsyH1MXIc+5e5B6CcijhitsGPUDRJjrJU2qg8bQi600='


if __name__ == '__main__':
    unittest.main()
