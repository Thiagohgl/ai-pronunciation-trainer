import unittest

import torch
from torchaudio.transforms import Resample

import pronunciationTrainer
from constants import sample_rate_start, sample_rate_resample
from lambdaSpeechToScore import audioread_load
from tests import EVENTS_FOLDER, set_seed

trainer_SST_lambda = {
    'de': pronunciationTrainer.getTrainer("de"),
    'en': pronunciationTrainer.getTrainer("en")
}
transform = Resample(orig_freq=sample_rate_start, new_freq=sample_rate_resample)


def helper_neural_asr(language: str):
    set_seed()
    signal, _ = audioread_load(EVENTS_FOLDER / f"test_{language}_easy.wav")
    signal_transformed = transform(torch.Tensor(signal)).unsqueeze(0)
    signal_transformed_preprocessed = pronunciationTrainer.preprocessAudioStandalone(signal_transformed)

    asr_model = trainer_SST_lambda[language].asr_model
    asr_model.processAudio(signal_transformed_preprocessed)
    audio_transcript = asr_model.getTranscript()
    word_locations_in_samples = asr_model.getWordLocations()
    return audio_transcript, word_locations_in_samples


class TestNeuralASR(unittest.TestCase):
    def setUp(self):
        import platform, os
        if platform.system() == "Windows" or platform.system() == "Win32":
            os.environ["PYTHONUTF8"] = "1"

    def test_neural_asr_de(self):
        self.maxDiff = None
        audio_transcript, word_locations_in_samples = helper_neural_asr("de")
        assert audio_transcript == ' Hallo, wie geht es dir?'
        assert word_locations_in_samples == [
            {'end_ts': 5120.0, 'start_ts': 0.0, 'word': ' Hallo,'},
            {'end_ts': 10240.0, 'start_ts': 8640.0, 'word': ' wie'},
            {'end_ts': 13120.0, 'start_ts': 10240.0, 'word': ' geht'},
            {'end_ts': 16640.0, 'start_ts': 13120.0, 'word': ' es'},
            {'end_ts': 20160.0, 'start_ts': 16640.0, 'word': ' dir?'}
        ]

    def test_neural_asr_en(self):
        self.maxDiff = None
        audio_transcript, word_locations_in_samples = helper_neural_asr("en")
        assert audio_transcript == ' Hi there, how are you?'
        assert word_locations_in_samples == [
            {'end_ts': 2240.0, 'start_ts': 0.0, 'word': ' Hi'},
            {'end_ts': 4800.0, 'start_ts': 2240.0, 'word': ' there,'},
            {'end_ts': 9280.0, 'start_ts': 7360.0, 'word': ' how'},
            {'end_ts': 11200.0, 'start_ts': 9280.0, 'word': ' are'},
            {'end_ts': 13760.0, 'start_ts': 11200.0, 'word': ' you?'}
        ]
