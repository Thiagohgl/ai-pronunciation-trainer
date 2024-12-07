import eng_to_ipa

from aip_trainer.models import ModelInterfaces
from aip_trainer import app_logger


class EpitranPhonemConverter(ModelInterfaces.ITextToPhonemModel):
    """
    A class to convert a given text to its phonemic representation using the Epitran library.

    Attributes:
    -----------
    word_locations_in_samples : None
        Placeholder attribute for word locations in samples.
    audio_transcript : None
        Placeholder attribute for audio transcript.
    epitran_model : object
        An instance of the Epitran model used for transliteration.
    """
    word_locations_in_samples = None
    audio_transcript = None

    def __init__(self, epitran_model) -> None:
        """Initializes the EpitranPhonemConverter with the given Epitran model."""
        super().__init__()
        self.epitran_model = epitran_model

    def convertToPhonem(self, sentence: str) -> str:
        """Converts a given sentence to its phonemic representation using the Epitran model."""
        app_logger.debug(f'starting EpitranPhonemConverter.convertToPhonem for sentence/token "{sentence}"...')
        phonem_representation = self.epitran_model.transliterate(sentence)
        app_logger.debug(f'EpitranPhonemConverter: got phonem_representation for sentence/token "{sentence}"!')
        return phonem_representation


class EngPhonemConverter(ModelInterfaces.ITextToPhonemModel):
    """
    A class to convert English sentences to their phonemic representation using the eng_to_ipa library.
    """

    def __init__(self,) -> None:
        """Initializes the EngPhonemConverter instance"""
        super().__init__()

    def convertToPhonem(self, sentence: str) -> str:
        """
        Converts a given English sentence to its phonemic representation.

        Parameters:
            sentence (str): The English sentence to be converted.
        Returns:
            str: The phonemic representation of the input sentence.
        """
        app_logger.debug(f'starting EngPhonemConverter.convertToPhonem for sentence/token "{sentence}"...')
        phonem_representation = eng_to_ipa.convert(sentence)
        phonem_representation = phonem_representation.replace('*','')
        app_logger.debug(f'EngPhonemConverter: got phonem_representation for sentence/token "{sentence}"!')
        return phonem_representation
