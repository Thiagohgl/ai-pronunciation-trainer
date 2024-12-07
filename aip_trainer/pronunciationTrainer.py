import time
from string import punctuation

import epitran
import numpy as np
import torch

from . import WordMatching as wm
from . import WordMetrics
from . import app_logger
from .models import AIModels, ModelInterfaces as mi, RuleBasedModels, models as mo


def preprocessAudioStandalone(audio: torch.tensor) -> torch.tensor:
    audio = audio-torch.mean(audio)
    audio = audio/torch.max(torch.abs(audio))
    return audio


class PronunciationTrainer:
    """
    A class used to train and evaluate pronunciation accuracy using ASR (Automatic Speech Recognition) and phoneme conversion models.

    Attributes
    ----------
    current_transcript : str
        The current transcript of the audio.
    current_ipa : str
        The current IPA (International Phonetic Alphabet) representation of the transcript.
    current_recorded_audio : torch.Tensor
        The current recorded audio tensor.
    current_recorded_transcript : str
        The transcript of the current recorded audio.
    current_recorded_word_locations : list
        The word locations in the current recorded audio.
    current_recorded_intonations : torch.tensor
        The intonations of the current recorded audio.
    current_words_pronunciation_accuracy : list
        The pronunciation accuracy of the current words.
    categories_thresholds : np.array
        The thresholds for categorizing pronunciation accuracy.
    sampling_rate : int
        The sampling rate of the audio.

    Methods
    -------
    __init__(asr_model: mi.IASRModel, word_to_ipa_coverter: mi.ITextToPhonemModel) -> None
        Initializes the PronunciationTrainer with ASR and phoneme conversion models.
    getTranscriptAndWordsLocations(audio_length_in_samples: int)
        Retrieves the transcript and word locations from the ASR model.
    getWordsRelativeIntonation(Audio: torch.tensor, word_locations: list)
        Calculates the relative intonation of words in the audio.
    processAudioForGivenText(recordedAudio: torch.Tensor = None, real_text=None)
        Processes the recorded audio and evaluates pronunciation accuracy against the given text.
    getAudioTranscript(recordedAudio: torch.Tensor = None)
        Retrieves the transcript, IPA, and word locations from the recorded audio.
    getWordLocationsFromRecordInSeconds(word_locations, mapped_words_indices) -> tuple[str, str]
        Converts word locations from samples to seconds.
    matchSampleAndRecordedWords(real_text, recorded_transcript)
        Matches the real text with the recorded transcript and retrieves the corresponding IPA.
    getPronunciationAccuracy(real_and_transcribed_words_ipa) -> tuple[float, list]
        Calculates the pronunciation accuracy based on the real and transcribed words' IPA.
    removePunctuation(word: str) -> str
        Removes punctuation from a given word.
    getWordsPronunciationCategory(accuracies) -> list
        Categorizes the pronunciation accuracy of words.
    getPronunciationCategoryFromAccuracy(accuracy) -> int
        Retrieves the pronunciation category based on accuracy.
    preprocessAudio(audio: torch.tensor) -> torch.tensor
        Preprocesses the audio by normalizing it.
    """
    current_transcript: str
    current_ipa: str

    current_recorded_audio: torch.Tensor
    current_recorded_transcript: str
    current_recorded_word_locations: list
    current_recorded_intonations: torch.tensor
    current_words_pronunciation_accuracy = []
    categories_thresholds = np.array([80, 60, 59])

    sampling_rate = 16000

    def __init__(self, asr_model: mi.IASRModel, word_to_ipa_coverter: mi.ITextToPhonemModel) -> None:
        self.asr_model = asr_model
        self.ipa_converter = word_to_ipa_coverter

    def getTranscriptAndWordsLocations(self, audio_length_in_samples: int):

        audio_transcript = self.asr_model.getTranscript()
        word_locations_in_samples = self.asr_model.getWordLocations()

        fade_duration_in_samples = 0.05*self.sampling_rate
        word_locations_in_samples = [(int(np.maximum(0, word['start_ts']-fade_duration_in_samples)), int(np.minimum(
            audio_length_in_samples-1, word['end_ts']+fade_duration_in_samples))) for word in word_locations_in_samples]

        return audio_transcript, word_locations_in_samples

    ##################### ASR Functions ###########################

    def processAudioForGivenText(self, recordedAudio: torch.Tensor = None, real_text=None):

        start = time.time()
        app_logger.info('starting getAudioTranscript...')
        recording_transcript, recording_ipa, word_locations = self.getAudioTranscript(recordedAudio)

        duration = time.time() - start
        app_logger.info(f'Time for NN to transcript audio: {duration}.')

        start = time.time()
        real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = self.matchSampleAndRecordedWords(
            real_text, recording_transcript)
        duration = time.time() - start
        app_logger.info(f'Time for matching transcripts: {duration}.')

        start_time, end_time = self.getWordLocationsFromRecordInSeconds(
            word_locations, mapped_words_indices)

        pronunciation_accuracy, current_words_pronunciation_accuracy = self.getPronunciationAccuracy(
            real_and_transcribed_words)  # _ipa

        pronunciation_categories = self.getWordsPronunciationCategory(
            current_words_pronunciation_accuracy)

        result = {'recording_transcript': recording_transcript,
                  'real_and_transcribed_words': real_and_transcribed_words,
                  'recording_ipa': recording_ipa, 'start_time': start_time, 'end_time': end_time,
                  'real_and_transcribed_words_ipa': real_and_transcribed_words_ipa, 'pronunciation_accuracy': pronunciation_accuracy,
                  'pronunciation_categories': pronunciation_categories}

        return result

    def getAudioTranscript(self, recordedAudio: torch.Tensor = None):
        current_recorded_audio = recordedAudio

        app_logger.info('starting preprocessAudio...')
        current_recorded_audio = self.preprocessAudio(current_recorded_audio)

        app_logger.info('starting processAudio...')
        self.asr_model.processAudio(current_recorded_audio)

        app_logger.info('starting getTranscriptAndWordsLocations...')
        current_recorded_transcript, current_recorded_word_locations = self.getTranscriptAndWordsLocations(
            current_recorded_audio.shape[1])
        app_logger.info('starting convertToPhonem...')
        current_recorded_ipa = self.ipa_converter.convertToPhonem(current_recorded_transcript)

        app_logger.info('ok, return audio transcript!')
        return current_recorded_transcript, current_recorded_ipa, current_recorded_word_locations

    def getWordLocationsFromRecordInSeconds(self, word_locations, mapped_words_indices) -> tuple[str, str]:
        start_time = []
        end_time = []
        for word_idx in range(len(mapped_words_indices)):
            start_time.append(float(word_locations[mapped_words_indices[word_idx]]
                                    [0])/self.sampling_rate)
            end_time.append(float(word_locations[mapped_words_indices[word_idx]]
                                  [1])/self.sampling_rate)
        return ' '.join([str(time) for time in start_time]), ' '.join([str(time) for time in end_time])

    ##################### END ASR Functions ###########################

    ##################### Evaluation Functions ###########################
    def matchSampleAndRecordedWords(self, real_text, recorded_transcript):
        words_estimated = recorded_transcript.split()

        if real_text is None:
            words_real = self.current_transcript[0].split()
        else:
            words_real = real_text.split()

        mapped_words, mapped_words_indices = wm.get_best_mapped_words(
            words_estimated, words_real)

        real_and_transcribed_words = []
        real_and_transcribed_words_ipa = []
        for word_idx in range(len(words_real)):
            if word_idx >= len(mapped_words)-1:
                mapped_words.append('-')
            real_and_transcribed_words.append(
                (words_real[word_idx],    mapped_words[word_idx]))
            real_and_transcribed_words_ipa.append((self.ipa_converter.convertToPhonem(words_real[word_idx]),
                                                   self.ipa_converter.convertToPhonem(mapped_words[word_idx])))
        return real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices

    def getPronunciationAccuracy(self, real_and_transcribed_words_ipa) -> tuple[float, list]:
        total_mismatches = 0.
        number_of_phonemes = 0.
        current_words_pronunciation_accuracy = []
        for pair in real_and_transcribed_words_ipa:

            real_without_punctuation = self.removePunctuation(pair[0]).lower()
            number_of_word_mismatches = WordMetrics.edit_distance_python(
                real_without_punctuation, self.removePunctuation(pair[1]).lower())
            total_mismatches += number_of_word_mismatches
            number_of_phonemes_in_word = len(real_without_punctuation)
            number_of_phonemes += number_of_phonemes_in_word

            current_words_pronunciation_accuracy.append(float(
                number_of_phonemes_in_word-number_of_word_mismatches)/number_of_phonemes_in_word*100)

        percentage_of_correct_pronunciations = (
            number_of_phonemes-total_mismatches)/number_of_phonemes*100

        return np.round(percentage_of_correct_pronunciations), current_words_pronunciation_accuracy

    def removePunctuation(self, word: str) -> str:
        return ''.join([char for char in word if char not in punctuation])

    def getWordsPronunciationCategory(self, accuracies) -> list:
        categories = []

        for accuracy in accuracies:
            categories.append(
                self.getPronunciationCategoryFromAccuracy(accuracy))

        return categories

    def getPronunciationCategoryFromAccuracy(self, accuracy) -> int:
        return np.argmin(abs(self.categories_thresholds-accuracy))

    def preprocessAudio(self, audio: torch.tensor) -> torch.tensor:
        return preprocessAudioStandalone(audio=audio)


def getTrainer(language: str) -> PronunciationTrainer:
    """
    Initializes and returns a PronunciationTrainer object for the specified language.

    Args:
        language (str): The language code for which the trainer is to be initialized.
                        Supported languages are 'de' for German and 'en' for English.

    Returns:
        PronunciationTrainer: An instance of the PronunciationTrainer class configured for the specified language.

    Raises:
        ValueError: If the specified language is not supported.

    """

    device = torch.device('cpu')

    model, decoder = mo.getASRModel(language)
    model = model.to(device)
    model.eval()
    asr_model = AIModels.NeuralASR(model, decoder)

    if language == 'de':
        epitran_deu_latn = epitran.Epitran('deu-Latn')
        phonem_converter = RuleBasedModels.EpitranPhonemConverter(epitran_deu_latn)
    elif language == 'en':
        phonem_converter = RuleBasedModels.EngPhonemConverter()
    else:
        raise ValueError('Language not implemented')

    trainer = PronunciationTrainer(asr_model, phonem_converter)

    return trainer
