import unittest
import numpy as np
from ModelInterfaces import IASRModel, ITranslationModel, ITextToSpeechModel, ITextToPhonemModel


class TestModelInterfaces(unittest.TestCase):
    def test_IASRModel(self):
        class ASRModel(IASRModel):
            def __init__(self):
                self.decoder = 1
                self.model = 2

            def getTranscript(self):
                return "transcript"

            def getWordLocations(self):
                return [(0, 1)]

            def processAudio(self, audio):
                return "processed audio"

        self.assertTrue(issubclass(ASRModel, IASRModel))
        asr_model = ASRModel()
        assert asr_model.decoder == 1
        assert asr_model.model == 2

    def test_ITranslationModel_subclasshook(self):
        class TranslationModel(ITranslationModel):
            def translateSentence(self, sentence):
                return "translated sentence"

        self.assertTrue(issubclass(TranslationModel, ITranslationModel))
        translation_model = TranslationModel()

    def test_ITextToSpeechModel_subclasshook(self):
        class TextToSpeechModel(ITextToSpeechModel):
            def getAudioFromSentence(self, sentence):
                return np.array([0.1, 0.2, 0.3])

        self.assertTrue(issubclass(TextToSpeechModel, ITextToSpeechModel))

    def test_ITextToPhonemModel_subclasshook(self):
        class TextToPhonemModel(ITextToPhonemModel):
            def convertToPhonem(self, sentence):
                return "phonemes"

        self.assertTrue(issubclass(TextToPhonemModel, ITextToPhonemModel))


if __name__ == '__main__':
    unittest.main()