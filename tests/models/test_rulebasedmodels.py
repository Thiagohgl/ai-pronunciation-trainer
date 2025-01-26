import unittest

import epitran
import RuleBasedModels


words_real = 'Ich habe sehr viel glück, am leben und gesund zu sein'
words_transcribed = 'Ic hab zeh viel guck am und gesund tu sein'


class TestPhonemConverter(unittest.TestCase):

    def test_english_ok(self):
        phonem_converter = RuleBasedModels.EngPhonemConverter()
        output = phonem_converter.convertToPhonem('Hello, this is a test')
        self.assertEqual(output, 'hɛˈloʊ, ðɪs ɪz ə tɛst')

    def test_german_ok(self):
        deu_latn = epitran.Epitran('deu-Latn')
        phonem_converter = RuleBasedModels.EpitranPhonemConverter(deu_latn)
        output = phonem_converter.convertToPhonem('Hallo, das ist ein Test')
        self.assertEqual(output, 'haloː, daːs ɪst aɪ̯n tɛst')


if __name__ == '__main__':
    unittest.main()
