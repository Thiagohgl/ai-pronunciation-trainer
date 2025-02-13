import unittest

import ModelInterfaces
import lambdaGetSample
import RuleBasedModels
import epitran
import json
import pronunciationTrainer
from tests import set_seed


def helper_category_test(category: int, threshold_min: int, threshold_max: int):
    event = {'body': json.dumps({'category': category, 'language': 'de'})}
    response = lambdaGetSample.lambda_handler(event, [])
    response_dict = json.loads(response)
    number_of_words = len(
        response_dict['real_transcript'][0].split())
    assert threshold_min < number_of_words <= threshold_max, f"Category {category} had a sentence with length {number_of_words}"


class TestDataset(unittest.TestCase):

    def test_random_sentences(self):
        expected_output__get_random_selection = {
            "de": {
                0: "Marie leidet an Hashimoto-Thyreoiditis.",
                1: "Marie leidet an Hashimoto-Thyreoiditis.",
                2: "Es ist einfach, den Status quo beibehalten; das heißt aber nicht, dass das auch das Richtige ist.",
                3: "Diana kam in 𝑖ℎ𝑟𝑒𝑚 zweitbesten Kleid vorbei und sah genauso aus, wie es sich ziemt, wenn man zum Tee geladen wird.",
            },
            "en": {
                0: "Mary has Hashimoto's.",
                1: "Mary has Hashimoto's.",
                2: "Following the status quo is easy, but that doesn't necessarily mean it's the right thing to do.",
                3: "Diana came over, dressed in HER second-best dress and looking exactly as it is proper to look when asked out to tea.",
            },
        }
        output_dict = {"de": {}, "en": {}}
        for lang in output_dict.keys():
            for cat in range(4):
                set_seed()
                event = {'body': json.dumps({'category': cat, 'language': lang})}
                response = lambdaGetSample.lambda_handler(event, [])
                response_dict = json.loads(response)
                output_dict[lang][cat] = response_dict["real_transcript"][0]
        self.assertDictEqual(output_dict, expected_output__get_random_selection)

    def test_easy_sentences(self):
        set_seed()
        helper_category_test(1, 0, 8)

    def test_normal_sentences(self):
        set_seed()
        helper_category_test(2, 8, 20)

    def test_hard_sentences(self):
        set_seed()
        helper_category_test(3, 20, 10000)


def check_phonem_converter(converter: ModelInterfaces.ITextToPhonemModel, input: str, expected_output: str):
    output = converter.convertToPhonem(input)
    assert output == expected_output, f'Conversion from "{input}" should be "{expected_output}", but was "{output}"'


class TestPhonemConverter(unittest.TestCase):

    def test_english(self):
        set_seed()
        phonem_converter = RuleBasedModels.EngPhonemConverter()
        check_phonem_converter(phonem_converter, 'Hello, this is a test', 'hɛˈloʊ, ðɪs ɪz ə tɛst')

    def test_german(self):
        set_seed()
        phonem_converter = RuleBasedModels.EpitranPhonemConverter(epitran.Epitran('deu-Latn'))
        check_phonem_converter(phonem_converter, 'Hallo, das ist ein Test', 'haloː, daːs ɪst aɪ̯n tɛst')


trainer_SST_lambda = {}
trainer_SST_lambda['de'] = pronunciationTrainer.getTrainer("de")


class TestScore(unittest.TestCase):

    def test_exact_transcription(self):
        set_seed()
        self.maxDiff = None
        words_real = 'Ich habe sehr viel glück, am leben und gesund zu sein'
        expected_accuracy = 100.0
        expected = {
            "matchSampleAndRecordedWords": {
                "real_and_transcribed_words": [('Ich', 'Ich'), ('habe', 'habe'), ('sehr', 'sehr'), ('viel', 'viel'), ('glück,', 'glück,'), ('am', 'am'), ('leben', 'leben'), ('und', 'und'), ('gesund', 'gesund'), ('zu', 'zu'), ('sein', 'sein')],
                "real_and_transcribed_words_ipa": [('ɪç', 'ɪç'), ('haːbə', 'haːbə'), ('zeːɐ̯', 'zeːɐ̯'), ('fiːl', 'fiːl'), ('ɡlyːk,', 'ɡlyːk,'), ('aːm', 'aːm'), ('lɛbn̩', 'lɛbn̩'), ('ʊnt', 'ʊnt'), ('ɡəzʊnt', 'ɡəzʊnt'), ('t͡suː', 't͡suː'), ('zaɪ̯n', 'zaɪ̯n')],
                "mapped_words_indices": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            },
            "getPronunciationAccuracy": {
                "pronunciation_accuracy": expected_accuracy,
                "current_words_pronunciation_accuracy": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0],
            },
        }

        real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = trainer_SST_lambda['de'].matchSampleAndRecordedWords(
            words_real, words_real)
        
        matchSampleAndRecordedWords_output = {
            "real_and_transcribed_words": real_and_transcribed_words,
            "real_and_transcribed_words_ipa": real_and_transcribed_words_ipa,
            "mapped_words_indices": mapped_words_indices
        }

        pronunciation_accuracy, current_words_pronunciation_accuracy = trainer_SST_lambda['de'].getPronunciationAccuracy(
            real_and_transcribed_words)

        getPronunciationAccuracy_output = {
            "pronunciation_accuracy": pronunciation_accuracy,
            "current_words_pronunciation_accuracy": current_words_pronunciation_accuracy
        }

        assert int(pronunciation_accuracy) == expected_accuracy, f"Expected {expected_accuracy}, got {pronunciation_accuracy}!"
        self.assertDictEqual(matchSampleAndRecordedWords_output, expected["matchSampleAndRecordedWords"])
        self.assertDictEqual(getPronunciationAccuracy_output, expected["getPronunciationAccuracy"])

    def test_incorrect_transcription(self):
        set_seed()
        self.maxDiff = None
        words_real = 'Ich habe sehr viel glück, am leben und gesund zu sein'
        words_transcribed = 'Ic hab zeh viel guck am und gesund tu sein'
        expected_accuracy = 67
        expected = {
            "matchSampleAndRecordedWords": {
                'real_and_transcribed_words': [('Ich', 'Ic'), ('habe', 'hab'), ('sehr', 'zeh'), ('viel', 'viel'), ('glück,', 'guck'), ('am', '-'), ('leben', 'am'), ('und', 'und'), ('gesund', 'gesund'), ('zu', 'tu'), ('sein', 'sein')],
                'real_and_transcribed_words_ipa': [('ɪç', 'iːk'), ('haːbə', 'haːp'), ('zeːɐ̯', 't͡seː'), ('fiːl', 'fiːl'), ('ɡlyːk,', 'kk'), ('aːm', '-'), ('lɛbn̩', 'aːm'), ('ʊnt', 'ʊnt'), ('ɡəzʊnt', 'ɡəzʊnt'), ('t͡suː', 'tuː'), ('zaɪ̯n', 'zaɪ̯n')],
                'mapped_words_indices': [0, 1, 2, 3, 4, -1, 5, 6, 7, 8, 9]},
            "getPronunciationAccuracy": {'pronunciation_accuracy': expected_accuracy, 'current_words_pronunciation_accuracy': [66.66666666666666, 75.0, 50.0, 100.0, 60.0, 0.0, 0.0, 100.0, 100.0, 50.0, 100.0]}
        }

        real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = trainer_SST_lambda['de'].matchSampleAndRecordedWords(
            words_real, words_transcribed)
        
        matchSampleAndRecordedWords_output = {
            "real_and_transcribed_words": real_and_transcribed_words,
            "real_and_transcribed_words_ipa": real_and_transcribed_words_ipa,
            "mapped_words_indices": mapped_words_indices
        }

        pronunciation_accuracy, current_words_pronunciation_accuracy = trainer_SST_lambda['de'].getPronunciationAccuracy(
            real_and_transcribed_words)

        getPronunciationAccuracy_output = {
            "pronunciation_accuracy": pronunciation_accuracy,
            "current_words_pronunciation_accuracy": current_words_pronunciation_accuracy
        }

        assert int(pronunciation_accuracy) == expected_accuracy, f"Expected {expected_accuracy}, got {pronunciation_accuracy}!"
        self.assertDictEqual(matchSampleAndRecordedWords_output, expected["matchSampleAndRecordedWords"])
        self.assertDictEqual(getPronunciationAccuracy_output, expected["getPronunciationAccuracy"])


if __name__ == '__main__':
    unittest.main()
