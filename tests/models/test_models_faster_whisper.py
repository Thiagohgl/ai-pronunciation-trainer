import unittest

import models as mo
import pronunciationTrainer
from tests.models.test_aimodels import helper_neural_asr


class TestModels(unittest.TestCase):

    def setUp(self):
        self.language_de = "de"
        self.language_en = "en"

    def test_getASRModel_de_whisper(self):
        from faster_whisper_wrapper import FasterWhisperASRModel
        asr = mo.getASRModel(self.language_de)
        self.assertIsInstance(asr, FasterWhisperASRModel)
        asr_explicit = mo.getASRModel(self.language_de, model_name="faster_whisper")
        self.assertIsInstance(asr_explicit, FasterWhisperASRModel)

    def test_getASRModel_en_whisper(self):
        from faster_whisper_wrapper import FasterWhisperASRModel
        asr = mo.getASRModel(self.language_en)
        self.assertIsInstance(asr, FasterWhisperASRModel)
        asr_explicit = mo.getASRModel(self.language_en, model_name="faster_whisper")
        self.assertIsInstance(asr_explicit, FasterWhisperASRModel)

    def test_neural_asr_de_faster_whisper(self):
        self.maxDiff = None
        audio_transcript, word_locations_in_samples = helper_neural_asr("de", "faster_whisper")
        assert audio_transcript == ' Hallo, wie geht es dir?'
        self.assertEqual(word_locations_in_samples, [
            {'end_ts': 5120.0, 'start_ts': 0.0, 'word': ' Hallo,'},
            {'end_ts': 10240.0, 'start_ts': 8640.0, 'word': ' wie'},
            {'end_ts': 13120.0, 'start_ts': 10240.0, 'word': ' geht'},
            {'end_ts': 16640.0, 'start_ts': 13120.0, 'word': ' es'},
            {'end_ts': 20160.0, 'start_ts': 16640.0, 'word': ' dir?'}
        ])

    def test_neural_asr_en_faster_whisper(self):
        self.maxDiff = None
        audio_transcript, word_locations_in_samples = helper_neural_asr("en", "faster_whisper")
        assert audio_transcript == ' Hi there, how are you?'
        self.assertEqual(word_locations_in_samples, [
            {'end_ts': 2240.0, 'start_ts': 0.0, 'word': ' Hi'},
            {'end_ts': 4800.0, 'start_ts': 2240.0, 'word': ' there,'},
            {'end_ts': 9280.0, 'start_ts': 7360.0, 'word': ' how'},
            {'end_ts': 11200.0, 'start_ts': 9280.0, 'word': ' are'},
            {'end_ts': 14080.0, 'start_ts': 11200.0, 'word': ' you?'}
        ])



if __name__ == '__main__':
    unittest.main()
