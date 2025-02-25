import ModelInterfaces
import torch
import numpy as np
import epitran
import eng_to_ipa

from constants import app_logger


def get_phonem_converter(language: str):
    """
    Get the phoneme converter for the specified language.

    Args:
        language (str): The language code (e.g., 'de' for German, 'en' for English).

    Returns:
        ModelInterfaces.ITextToPhonemModel: The phoneme converter for the specified language.

    Raises:
        ValueError: If the language is not implemented.
    """
    if language == 'de':
        phonem_converter = EpitranPhonemConverter(
            epitran.Epitran('deu-Latn'))
    elif language == 'en':
        phonem_converter = EngPhonemConverter()
    else:
        raise ValueError('Language not implemented')

    return phonem_converter

class EpitranPhonemConverter(ModelInterfaces.ITextToPhonemModel):
    """
    A phoneme converter using the Epitran library for transliteration.
    """
    word_locations_in_samples = None
    audio_transcript = None

    def __init__(self, epitran_model) -> None:
        """
        Initialize the EpitranPhonemConverter with an Epitran model.

        Args:
            epitran_model: The Epitran model for transliteration.
        """
        super().__init__()
        self.epitran_model = epitran_model

    def convertToPhonem(self, sentence: str) -> str:
        """
        Convert a sentence to its phoneme representation.

        Args:
            sentence (str): The input sentence.

        Returns:
            str: The phoneme representation of the sentence.
        """
        app_logger.debug(f'starting EpitranPhonemConverter.convertToPhonem for sentence/token "{sentence}"...')
        phonem_representation = self.epitran_model.transliterate(sentence)
        app_logger.debug(f'EpitranPhonemConverter: got phonem_representation for sentence/token "{sentence}"!')
        return phonem_representation


class EngPhonemConverter(ModelInterfaces.ITextToPhonemModel):
    """
    A phoneme converter for English using the eng\_to\_ipa library.
    """

    def __init__(self,) -> None:
        """
        Initialize the EngPhonemConverter.
        """
        super().__init__()

    def convertToPhonem(self, sentence: str) -> str:
        """
        Convert a sentence to its phoneme representation.

        Args:
            sentence (str): The input sentence.

        Returns:
            str: The phoneme representation of the sentence.
        """
        app_logger.debug(f'starting EngPhonemConverter.convertToPhonem for sentence/token "{sentence}"...')
        phonem_representation = eng_to_ipa.convert(sentence)
        phonem_representation = phonem_representation.replace('*','')
        app_logger.debug(f'EngPhonemConverter: got phonem_representation for sentence/token "{sentence}"!')
        return phonem_representation
