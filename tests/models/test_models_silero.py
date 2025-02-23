import unittest
import torch
import torch.package
from transformers import MarianTokenizer

import models as mo
from AIModels import NeuralASR
from constants import sample_rate_resample, language_not_implemented


class TestModels(unittest.TestCase):

    def setUp(self):
        self.language_de = "de"
        self.language_en = "en"
        self.tmp_dir = torch.hub.get_dir()
        self.device = torch.device("cpu")

    def test_getASRModel_de_silero(self):
        asr = mo.getASRModel(self.language_de, model_name="silero")
        self.assertIsInstance(asr, NeuralASR)

    def test_getASRModel_en_silero(self):
        asr = mo.getASRModel(self.language_en, model_name="silero")
        self.assertIsInstance(asr, NeuralASR)

    def test_getASRModel_language_not_implemented(self):
        with self.assertRaises(ValueError):
            lang = "wrong_language"
            try:
                mo.getASRModel(lang, model_name="silero")
            except ValueError as ve:
                msg = language_not_implemented.format(lang)
                self.assertEqual(str(ve), msg)
                raise ve

    def test_getASRModel_model_not_implemented(self):
        with self.assertRaises(ValueError):
            model = "wrong_model"
            try:
                mo.getASRModel(self.language_de, model_name=model)
            except ValueError as ve:
                msg = f"Model '{model}' not implemented. Supported models: whisper, faster_whisper, silero."
                self.assertEqual(str(ve), msg)
                raise ve

    def test_getTranslationModel_de(self):
        model, tokenizer = mo.getTranslationModel(self.language_de)
        self.assertIsInstance(model, torch.nn.Module)
        self.assertIsInstance(tokenizer, MarianTokenizer)

    def test_getTranslationModel_not_implemented(self):
        with self.assertRaises(ValueError):
            lang = "wrong_language"
            try:
                mo.getTranslationModel(lang)
            except ValueError as ve:
                self.assertEqual(str(ve), language_not_implemented.format(lang))
                raise ve

    def test_whisper_wrapper_parse_word(self):
        from whisper_wrapper import parse_word_info

        inputs_list = [
            {'word': ' Hallo,', 'start': 0.0, 'end': 0.32, 'probability': 0.8968557715415955},
            {'word': ' wie', 'start': 0.54, 'end': 0.64, 'probability': 0.9032214879989624},
            {'word': ' geht', 'start': 0.64, 'end': 0.82, 'probability': 0.9981840252876282},
            {'word': ' es', 'start': 0.82, 'end': 1.04, 'probability': 0.9160193800926208},
            {'word': ' dir?', 'start': 1.04, 'end': 1.26, 'probability': 0.9904420971870422}
        ]
        expected_outputs_list = [
            {'word': ' Hallo,', 'start_ts': 0.0, 'end_ts': 5120.0},
            {'word': ' wie', 'start_ts': 8640.0, 'end_ts': 10240.0},
            {'word': ' geht', 'start_ts': 10240.0, 'end_ts': 13120.0},
            {'word': ' es', 'start_ts': 13120.0, 'end_ts': 16640.0},
            {'word': ' dir?', 'start_ts': 16640.0, 'end_ts': 20160.0}
        ]
        for word_info, expected_output in zip(inputs_list, expected_outputs_list):
            output = parse_word_info(
                word_info=word_info,
                sample_rate=sample_rate_resample
            )
            print(f"output: {output} .")
            self.assertEqual(output, expected_output)


if __name__ == '__main__':
    unittest.main()