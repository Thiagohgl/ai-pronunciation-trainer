import ModelInterfaces
import torch
import numpy as np
import epitran
import eng_to_ipa


class EpitranPhonemConverter(ModelInterfaces.ITextToPhonemModel):
    word_locations_in_samples = None
    audio_transcript = None

    def __init__(self, epitran_model) -> None:
        super().__init__()
        self.epitran_model = epitran_model

    def convertToPhonem(self, sentence: str) -> str:
        phonem_representation = self.epitran_model.transliterate(sentence)
        return phonem_representation


class EngPhonemConverter(ModelInterfaces.ITextToPhonemModel):

    def __init__(self,) -> None:
        super().__init__()

    def convertToPhonem(self, sentence: str) -> str:
        phonem_representation = eng_to_ipa.convert(sentence)
        phonem_representation = phonem_representation.replace('*','')
        return phonem_representation
