import unittest

import torch
from torchaudio.transforms import Resample

import pronunciationTrainer
from constants import sample_rate_start, sample_rate_resample, MODEL_NAME_DEFAULT
from lambdaSpeechToScore import audioread_load
from tests import EVENTS_FOLDER, set_seed


trainer_sst_lambda = {
    'de': pronunciationTrainer.getTrainer("de"),
    'en': pronunciationTrainer.getTrainer("en")
}
transform = Resample(orig_freq=sample_rate_start, new_freq=sample_rate_resample)


def helper_neural_asr(language: str, model_name: str):
    import models as mo
    set_seed()
    signal, _ = audioread_load(EVENTS_FOLDER / f"test_{language}_easy.wav")
    signal_transformed = transform(torch.Tensor(signal)).unsqueeze(0)
    signal_transformed_preprocessed = pronunciationTrainer.preprocessAudioStandalone(signal_transformed)

    asr_model = mo.getASRModel(language, model_name=model_name)
    asr_model.processAudio(signal_transformed_preprocessed)
    audio_transcript = asr_model.getTranscript()
    word_locations_in_samples = asr_model.getWordLocations()
    return audio_transcript, word_locations_in_samples


class TestNeuralASR(unittest.TestCase):
    def setUp(self):
        import platform
        import os
        if platform.system() == "Windows" or platform.system() == "Win32":
            os.environ["PYTHONUTF8"] = "1"
            os.environ["IS_TESTING"] = "TRUE"

    def tearDown(self):
        import platform
        import os
        if platform.system() == "Windows" or platform.system() == "Win32" and "PYTHONUTF8" in os.environ:
            del os.environ["PYTHONUTF8"]
            del os.environ["IS_TESTING"]

    def test_neural_asr_de_whisper(self):
        self.maxDiff = None
        for model_name in [MODEL_NAME_DEFAULT, "whisper"]:
            audio_transcript, word_locations_in_samples = helper_neural_asr("de", model_name)
            assert audio_transcript == ' Hallo, wie geht es dir?'
            self.assertEqual(word_locations_in_samples, [
                {'end_ts': 5120.0, 'start_ts': 0.0, 'word': ' Hallo,'},
                {'end_ts': 10240.0, 'start_ts': 8640.0, 'word': ' wie'},
                {'end_ts': 13120.0, 'start_ts': 10240.0, 'word': ' geht'},
                {'end_ts': 16640.0, 'start_ts': 13120.0, 'word': ' es'},
                {'end_ts': 20160.0, 'start_ts': 16640.0, 'word': ' dir?'}
            ])

    def test_neural_asr_en_default(self):
        self.maxDiff = None
        for model_name in [MODEL_NAME_DEFAULT, "whisper"]:
            audio_transcript, word_locations_in_samples = helper_neural_asr("en", model_name)
            assert audio_transcript == ' Hi there, how are you?'
            self.assertEqual(word_locations_in_samples, [
                {'end_ts': 2240.0, 'start_ts': 0.0, 'word': ' Hi'},
                {'end_ts': 4800.0, 'start_ts': 2240.0, 'word': ' there,'},
                {'end_ts': 9280.0, 'start_ts': 7360.0, 'word': ' how'},
                {'end_ts': 11200.0, 'start_ts': 9280.0, 'word': ' are'},
                {'end_ts': 13760.0, 'start_ts': 11200.0, 'word': ' you?'}
            ])

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

    def test_neural_asr_de_silero(self):
        self.maxDiff = None
        audio_transcript, word_locations_in_samples = helper_neural_asr("de", "silero")
        assert audio_transcript == 'hallo wie geht es dir'
        print("word_locations_in_samples:")
        print(word_locations_in_samples)
        self.assertEqual(word_locations_in_samples, [
            {'word': 'hallo', 'start_ts': 0.0, 'end_ts': 6773.68},
            {'word': 'wie', 'start_ts': 6773.68, 'end_ts': 10468.42},
            {'word': 'geht', 'start_ts': 10468.42, 'end_ts': 13547.37},
            {'word': 'es', 'start_ts': 13547.37, 'end_ts': 16626.32},
            {'word': 'dir', 'start_ts': 16626.32, 'end_ts': 20321.05}
        ])

    def test_neural_asr_en_silero(self):
        self.maxDiff = None
        audio_transcript, word_locations_in_samples = helper_neural_asr("en", "silero")
        assert audio_transcript == 'i there how are you'
        self.assertEqual(word_locations_in_samples, [
            {'end_ts': 1800.0, 'start_ts': 0.0, 'word': 'i'},
            {'end_ts': 5400.0, 'start_ts': 1800.0, 'word': 'there'},
            {'end_ts': 8400.0, 'start_ts': 5400.0, 'word': 'how'},
            {'end_ts': 12000.0, 'start_ts': 8400.0, 'word': 'are'},
            {'end_ts': 15000.0, 'start_ts': 12000.0, 'word': 'you'}
        ])


if __name__ == '__main__':
    unittest.main()