import tempfile
import unittest
import torch
from pathlib import Path
from silero.utils import Decoder
from silero.silero import silero_tts
import torch.package
from aip_trainer import PROJECT_ROOT_FOLDER
from aip_trainer.models import models as mo

class TestModels(unittest.TestCase):

    def setUp(self):
        self.language_de = "de"
        self.language_en = "en"
        self.tmp_dir = torch.hub.get_dir()
        self.device = torch.device("cpu")

    def test_getASRModel_de(self):
        model, decoder = mo.getASRModel(self.language_de)
        self.assertIsInstance(model, torch.nn.Module)
        self.assertIsInstance(decoder, Decoder)

    def test_getASRModel_en(self):
        model, decoder = mo.getASRModel(self.language_en)
        self.assertIsInstance(model, torch.nn.Module)
        self.assertIsInstance(decoder, Decoder)

    def test_silero_stt_en(self):
        model, decoder, utils = mo.silero_stt(language=self.language_en, output_folder=self.tmp_dir)
        self.assertIsInstance(model, torch.jit.ScriptModule)
        self.assertIsInstance(decoder, Decoder)
        self.assertIsInstance(utils, tuple)

    def test_silero_tts_en2(self):
        model, example, speaker, sample_rate = mo.silero_tts(language=self.language_en, output_folder=self.tmp_dir)
        assert model is not None
        self.assertIsInstance(model, object)
        self.assertIsInstance(example, str)
        self.assertIsInstance(speaker, str)
        self.assertIsInstance(sample_rate, int)
        assert speaker == 'en_0'
        assert sample_rate == 48000
        assert example == 'Can you can a canned can into an un-canned can like a canner can can a canned can into an un-canned can?'

    def test_init_jit_model_en(self):
        name = "en_v5.jit"
        model_url_en = f'https://models.silero.ai/models/en/{name}'
        model_en1, decoder_en1 = mo.init_jit_model(model_url_en, device=self.device, output_folder=self.tmp_dir)
        self.assertIsInstance(model_en1, torch.nn.Module)
        self.assertIsInstance(decoder_en1, Decoder)

        model_en2, decoder_en2 = mo.init_jit_model(model_url_en, device=self.device)
        self.assertIsInstance(model_en2, torch.nn.Module)
        self.assertIsInstance(decoder_en2, Decoder)
        # model_en_filepath.unlink(missing_ok=False)
        
        model_en3, decoder_en3 = mo.init_jit_model(model_url_en)
        self.assertIsInstance(model_en3, torch.nn.Module)
        self.assertIsInstance(decoder_en3, Decoder)
        # model_en_filepath.unlink(missing_ok=False)

    def test_get_models_de(self):
        models_de = mo.get_models(self.language_de, self.tmp_dir, "latest", "stt_models")
        self.assertIn(self.language_de, models_de.stt_models)

    def test_get_models_en(self):
        models_en = mo.get_models(self.language_en, self.tmp_dir, "latest", "stt_models")
        self.assertIn(self.language_en, models_en.stt_models)

    def test_get_latest_model_de(self):
        model_de, decoder_de = mo.get_latest_model(self.language_de, self.tmp_dir, "latest", "stt_models", "jit")
        self.assertIsInstance(model_de, torch.nn.Module)
        self.assertIsInstance(decoder_de, Decoder)

    def test_get_latest_model_en(self):
        model_en, decoder_en = mo.get_latest_model(self.language_en, self.tmp_dir, "latest", "stt_models", "jit")
        self.assertIsInstance(model_en, torch.nn.Module)
        self.assertIsInstance(decoder_en, Decoder)

    def test_get_latest_stt_model_de(self):
        model_de, decoder_de = mo.get_latest_stt_model(self.language_de, self.tmp_dir, "latest", "stt_models", "jit")
        self.assertIsInstance(model_de, torch.nn.Module)
        self.assertIsInstance(decoder_de, Decoder)

    def test_get_latest_stt_model_en(self):
        model_en, decoder_en = mo.get_latest_stt_model(self.language_en, self.tmp_dir, "latest", "stt_models", "jit")
        self.assertIsInstance(model_en, torch.nn.Module)
        self.assertIsInstance(decoder_en, Decoder)

if __name__ == '__main__':
    unittest.main()