import unittest

import models as mo
import pronunciationTrainer


trainer_sst_lambda = {
    'de': pronunciationTrainer.getTrainer("de"),
    'en': pronunciationTrainer.getTrainer("en")
}


class TestModels(unittest.TestCase):

    def setUp(self):
        self.language_de = "de"
        self.language_en = "en"

    def test_getASRModel_de_whisper(self):
        from whisper_wrapper import WhisperASRModel
        asr = mo.getASRModel(self.language_de)
        self.assertIsInstance(asr, WhisperASRModel)
        asr_explicit = mo.getASRModel(self.language_de, model_name="whisper")
        self.assertIsInstance(asr_explicit, WhisperASRModel)

    def test_getASRModel_en_whisper(self):
        from whisper_wrapper import WhisperASRModel
        asr = mo.getASRModel(self.language_en)
        self.assertIsInstance(asr, WhisperASRModel)
        asr_explicit = mo.getASRModel(self.language_en, model_name="whisper")
        self.assertIsInstance(asr_explicit, WhisperASRModel)

    def test_whisper_wrapper_processAudio_and_get_outputs_de(self):
        from tests.models.test_aimodels import helper_neural_asr
        audio_transcript, word_locations_in_samples = helper_neural_asr("de", trainer_sst_lambda)
        assert audio_transcript == ' Hallo, wie geht es dir?'
        assert word_locations_in_samples == [
            {'end_ts': 5120.0, 'start_ts': 0.0, 'word': ' Hallo,'},
            {'end_ts': 10240.0, 'start_ts': 8640.0, 'word': ' wie'},
            {'end_ts': 13120.0, 'start_ts': 10240.0, 'word': ' geht'},
            {'end_ts': 16640.0, 'start_ts': 13120.0, 'word': ' es'},
            {'end_ts': 20160.0, 'start_ts': 16640.0, 'word': ' dir?'}
        ]

    def test_whisper_wrapper_processAudio_and_get_outputs_en(self):
        from tests.models.test_aimodels import helper_neural_asr
        audio_transcript, word_locations_in_samples = helper_neural_asr("en", trainer_sst_lambda)
        assert audio_transcript == ' Hi there, how are you?'
        assert word_locations_in_samples == [
            {'end_ts': 2240.0, 'start_ts': 0.0, 'word': ' Hi'},
            {'end_ts': 4800.0, 'start_ts': 2240.0, 'word': ' there,'},
            {'end_ts': 9280.0, 'start_ts': 7360.0, 'word': ' how'},
            {'end_ts': 11200.0, 'start_ts': 9280.0, 'word': ' are'},
            {'end_ts': 13760.0, 'start_ts': 11200.0, 'word': ' you?'}
        ]


if __name__ == '__main__':
    unittest.main()

