import json
import unittest
import torch

from torchaudio.transforms import Resample

from aip_trainer.lambdas.lambdaSpeechToScore import soundfile_load
from aip_trainer.models import AIModels, models as mo
from aip_trainer import sample_rate_start
from aip_trainer.pronunciationTrainer import preprocessAudioStandalone
from aip_trainer.utils import utilities
from tests import EVENTS_FOLDER
from tests.lambdas.test_lambdaSpeechToScore import set_seed


device = torch.device('cpu')
transform = Resample(orig_freq=sample_rate_start, new_freq=16000)


def get_model(language):
    model, decoder = mo.getASRModel(language)
    model = model.to(device)
    model.eval()
    return AIModels.NeuralASR(model, decoder)

signal_de, samplerate = soundfile_load(str(EVENTS_FOLDER / "test_de_easy.wav"))
signal_en, samplerate = soundfile_load(str(EVENTS_FOLDER / "test_en_easy.wav"))
signal_transformed_de = transform(torch.Tensor(signal_de)).unsqueeze(0)
signal_transformed_de = preprocessAudioStandalone(signal_transformed_de)
signal_transformed_en = transform(torch.Tensor(signal_en)).unsqueeze(0)
signal_transformed_en = preprocessAudioStandalone(signal_transformed_en)


class TestDeNeuralASR(unittest.TestCase):
    def test_is_instance_of_NeuralASR_language_de(self):
        asr_de = get_model("de")
        self.assertIsInstance(asr_de, AIModels.NeuralASR)

    def test_is_instance_of_NeuralASR_language_en(self):
        asr_en = get_model("de")
        self.assertIsInstance(asr_en, AIModels.NeuralASR)

    def test_getTranscript_without_processing_audio_de(self):
        with self.assertRaises(AssertionError):
            try:
                asr_de = get_model("de")
                asr_de.getTranscript()
            except AssertionError as ae:
                assert "Can get audio transcripts without having processed the audio" in str(ae)
                raise ae

    def test_getTranscript_without_processing_audio_en(self):
        with self.assertRaises(AssertionError):
            try:
                asr_en = get_model("en")
                asr_en.getTranscript()
            except AssertionError as ae:
                assert "Can get audio transcripts without having processed the audio" in str(ae)
                raise ae

    def test_getWordLocations_without_processing_audio_de(self):
        with self.assertRaises(AssertionError):
            try:
                asr_de = get_model("de")
                asr_de.getWordLocations()
            except AssertionError as ae:
                assert "Can get word locations without having processed the audio" in str(ae)
                raise ae

    def test_getWordLocations_without_processing_audio_en(self):
        with self.assertRaises(AssertionError):
            try:
                asr_en = get_model("en")
                asr_en.getWordLocations()
            except AssertionError as ae:
                assert "Can get word locations without having processed the audio" in str(ae)
                raise ae

    def test_process_audio_de(self):
        set_seed()
        asr_de = get_model("de")
        self.assertIsNone(asr_de.audio_transcript)
        self.assertIsNone(asr_de.word_locations_in_samples)

        asr_de.processAudio(signal_transformed_de)

        self.assertEqual(asr_de.audio_transcript, 'hallo wie geht es dir')
        self.assertEqual(
            asr_de.word_locations_in_samples,
            [
                {"word": "hallo", "start_ts": 0.0, "end_ts": 6773.68},
                {"word": "wie", "start_ts": 6773.68, "end_ts": 10468.42},
                {"word": "geht", "start_ts": 10468.42, "end_ts": 13547.37},
                {"word": "es", "start_ts": 13547.37, "end_ts": 16626.32},
                {"word": "dir", "start_ts": 16626.32, "end_ts": 20321.05},
            ],
        )

    def test_process_audio_en(self):
        set_seed()
        asr_en = get_model("en")
        self.assertIsNone(asr_en.audio_transcript)
        self.assertIsNone(asr_en.word_locations_in_samples)

        asr_en.processAudio(signal_transformed_en)

        self.assertEqual(asr_en.audio_transcript, 'i there how are you')
        self.assertEqual(
            asr_en.word_locations_in_samples,
            [
                {"word": "i", "start_ts": 0.0, "end_ts": 1800.0},
                {"word": "there", "start_ts": 1800.0, "end_ts": 5400.0},
                {"word": "how", "start_ts": 5400.0, "end_ts": 8400.0},
                {"word": "are", "start_ts": 8400.0, "end_ts": 12000.0},
                {"word": "you", "start_ts": 12000.0, "end_ts": 15000.0},
            ],
        )

    def test_getTranscript_after_processing_audio_de(self):
        set_seed()
        asr_de = get_model("de")
        asr_de.processAudio(signal_transformed_de)
        transcript = asr_de.getTranscript()
        self.assertEqual(transcript, 'hallo wie geht es dir')

    def test_getTranscript_after_processing_audio_en(self):
        set_seed()
        asr_en = get_model("en")
        asr_en.processAudio(signal_transformed_en)
        transcript = asr_en.getTranscript()
        self.assertEqual(transcript, 'i there how are you')

    def test_getWordLocations_after_processing_audio_de(self):
        set_seed()
        asr_de = get_model("de")
        asr_de.processAudio(signal_transformed_de)
        word_locations = asr_de.getWordLocations()
        self.assertEqual(
            word_locations,
            [
                {"word": "hallo", "start_ts": 0.0, "end_ts": 6773.68},
                {"word": "wie", "start_ts": 6773.68, "end_ts": 10468.42},
                {"word": "geht", "start_ts": 10468.42, "end_ts": 13547.37},
                {"word": "es", "start_ts": 13547.37, "end_ts": 16626.32},
                {"word": "dir", "start_ts": 16626.32, "end_ts": 20321.05},
            ],
        )

    def test_getWordLocations_after_processing_audio_en(self):
        set_seed()
        asr_en = get_model("en")
        asr_en.processAudio(signal_transformed_en)
        word_locations = asr_en.getWordLocations()
        self.assertEqual(
            word_locations,
            [
                {"word": "i", "start_ts": 0.0, "end_ts": 1800.0},
                {"word": "there", "start_ts": 1800.0, "end_ts": 5400.0},
                {"word": "how", "start_ts": 5400.0, "end_ts": 8400.0},
                {"word": "are", "start_ts": 8400.0, "end_ts": 12000.0},
                {"word": "you", "start_ts": 12000.0, "end_ts": 15000.0},
            ],
        )


if __name__ == '__main__':
    unittest.main()
