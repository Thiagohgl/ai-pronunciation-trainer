import abc

import numpy as np


class IASRModel(metaclass=abc.ABCMeta):
    """
    IASRModel is an abstract base class that defines the interface for Automatic Speech Recognition (ASR) models.

    Methods
    -------
    getTranscript() -> str
        Abstract method to get the transcript of the processed audio.

    getWordLocations() -> list
        Abstract method to get the locations of words in the audio.

    processAudio(audio)
        Abstract method to process the audio input.
    """
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
    """
    Interface for translation models.

    This interface defines the structure for translation models, ensuring that any subclass implements the required methods.

    Methods
    -------
    translateSentence(str) -> str
        Abstract method to get the translation of the sentence. Must be implemented by any subclass.

    __subclasshook__(cls, subclass)
        Class method to check if a class is considered a subclass of ITranslationModel based on the presence of the 'translateSentence' method.
    """
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'translateSentence') and
                callable(subclass.translateSentence))

    @abc.abstractmethod
    def translateSentence(self, str) -> str:
        """Get the translation of the sentence"""
        raise NotImplementedError


class ITextToSpeechModel(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'getAudioFromSentence') and
                callable(subclass.getAudioFromSentence))

    @abc.abstractmethod
    def getAudioFromSentence(self, str) -> np.array:
        """Get audio from sentence"""
        raise NotImplementedError


class ITextToPhonemModel(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'convertToPhonem') and
                callable(subclass.convertToPhonem))

    @abc.abstractmethod
    def convertToPhonem(self, str) -> str:
        """Convert sentence to phonemes"""
        raise NotImplementedError
