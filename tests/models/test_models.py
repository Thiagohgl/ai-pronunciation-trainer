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

    def test_getASRModel_de(self):
        asr = mo.getASRModel(self.language_de, use_whisper=False)
        self.assertIsInstance(asr, NeuralASR)

    def test_getASRModel_en(self):
        asr = mo.getASRModel(self.language_en, use_whisper=False)
        self.assertIsInstance(asr, NeuralASR)

    def test_getTranslationModel_de(self):
        model, tokenizer = mo.getTranslationModel(self.language_de)
        self.assertIsInstance(model, torch.nn.Module)
        self.assertIsInstance(tokenizer, MarianTokenizer)

if __name__ == '__main__':
    unittest.main()

