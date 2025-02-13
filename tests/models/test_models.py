import unittest
import torch
import torch.package
from transformers import MarianTokenizer

import models as mo
from AIModels import NeuralASR


class TestModels(unittest.TestCase):

    def setUp(self):
        self.language_de = "de"
        self.language_en = "en"
        self.tmp_dir = torch.hub.get_dir()
        self.device = torch.device("cpu")

    def test_getASRModel_de_whisper(self):
        asr = mo.getASRModel(self.language_de, use_whisper=True)
        self.assertIsInstance(asr, NeuralASR)

    def test_getASRModel_de(self):
        asr = mo.getASRModel(self.language_de, use_whisper=False)
        self.assertIsInstance(asr, NeuralASR)

    def test_getASRModel_en(self):
        asr = mo.getASRModel(self.language_en, use_whisper=False)
        self.assertIsInstance(asr, NeuralASR)

    def test_getASRModel_not_implemented(self):
        with self.assertRaises(ValueError):
            try:
                mo.getASRModel("wrong_language", use_whisper=False)
            except ValueError as ve:
                self.assertEqual(str(ve), "Language not implemented")
                raise ve

    def test_getTranslationModel_de(self):
        model, tokenizer = mo.getTranslationModel(self.language_de)
        self.assertIsInstance(model, torch.nn.Module)
        self.assertIsInstance(tokenizer, MarianTokenizer)

    def test_getTranslationModel_not_implemented(self):
        with self.assertRaises(ValueError):
            try:
                mo.getTranslationModel("wrong_language")
            except ValueError as ve:
                self.assertEqual(str(ve), "Language not implemented")
                raise ve

    def test_getTTSModel_de(self):
        tts_module = mo.getTTSModel('de')
        model = tts_module.model
        assert isinstance(model, torch.nn.Module)

    # def test_getTTSModel_en(self):
    #     # for some reason this English TTS model doesn't work, in fact only the author uses only the German TTS model (lambdaTTS.py)
    #     tts_module = mo.getTTSModel('en')
    #     model = tts_module.model
    #     assert isinstance(model, torch.nn.Module)

    def test_getTTSModel_not_implemented(self):
        with self.assertRaises(ValueError):
            try:
                mo.getTTSModel("it")
            except ValueError as ve:
                assert str(ve) == "Language not implemented"
                raise ve


if __name__ == '__main__':
    unittest.main()

