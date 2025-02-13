import unittest

import epitran
import RuleBasedModels


words_real = 'Ich habe sehr viel glück, am leben und gesund zu sein'
words_transcribed = 'Ic hab zeh viel guck am und gesund tu sein'


class TestPhonemConverter(unittest.TestCase):
    def test_get_phonem_converter_de(self):
        converter = RuleBasedModels.get_phonem_converter('de')
        self.assertIsInstance(converter, RuleBasedModels.EpitranPhonemConverter)

    def test_get_phonem_converter_en(self):
        converter = RuleBasedModels.get_phonem_converter('en')
        self.assertIsInstance(converter, RuleBasedModels.EngPhonemConverter)

    def test_get_phonem_converter_invalid_language(self):
        with self.assertRaises(ValueError):
            try:
                RuleBasedModels.get_phonem_converter('fr')
            except ValueError as ve:
                self.assertEqual(str(ve), 'Language not implemented')
                raise ve

    def test_converttophonem_de(self):
        phonem_converter = RuleBasedModels.EngPhonemConverter()
        output = phonem_converter.convertToPhonem('Hello, this is a test')
        self.assertEqual(output, 'hɛˈloʊ, ðɪs ɪz ə tɛst')

    def test_converttophonem_en(self):
        deu_latn = epitran.Epitran('deu-Latn')
        phonem_converter = RuleBasedModels.EpitranPhonemConverter(deu_latn)
        output = phonem_converter.convertToPhonem('Hallo, das ist ein Test')
        self.assertEqual(output, 'haloː, daːs ɪst aɪ̯n tɛst')


if __name__ == '__main__':
    unittest.main()
