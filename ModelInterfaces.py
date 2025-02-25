
import abc
import numpy as np


class IASRModel(metaclass=abc.ABCMeta):
    """Automatic Speech Recognition Model Interface"""
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'getTranscript') and
                callable(subclass.getTranscript) and
                hasattr(subclass, 'getWordLocations') and
                callable(subclass.getWordLocations) and
                hasattr(subclass, 'processAudio') and
                callable(subclass.processAudio))

    @abc.abstractmethod
    def getTranscript(self) -> str:
        """Get the transcripts of the process audio"""
        raise NotImplementedError

    @abc.abstractmethod
    def getWordLocations(self) -> list:
        """Get the pair of words location from audio"""
        raise NotImplementedError

    @abc.abstractmethod
    def processAudio(self, audio):
        """Process the audio"""
        raise NotImplementedError


class ITranslationModel(metaclass=abc.ABCMeta):
    """Translation model"""
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'translateSentence') and
                callable(subclass.translateSentence))

    @abc.abstractmethod
    def translateSentence(self, str) -> str:
        """Get the translation of the sentence"""
        raise NotImplementedError


class ITextToSpeechModel(metaclass=abc.ABCMeta):
    """Text to Speech model"""
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'getAudioFromSentence') and
                callable(subclass.getAudioFromSentence))

    @abc.abstractmethod
    def getAudioFromSentence(self, str) -> np.array:
        """Get audio from sentence"""
        raise NotImplementedError


class ITextToPhonemModel(metaclass=abc.ABCMeta):
    """Text to Phonem model, needed to evaluate the correctness of speech pronunciation"""
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'convertToPhonem') and
                callable(subclass.convertToPhonem))

    @abc.abstractmethod
    def convertToPhonem(self, str) -> str:
        """Convert sentence to phonemes"""
        raise NotImplementedError
