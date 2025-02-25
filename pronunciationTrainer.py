import time
from string import punctuation

import epitran
import numpy as np
import torch

import ModelInterfaces as mi
import RuleBasedModels
import WordMatching as wm
import WordMetrics
import models as mo
from constants import app_logger, MODEL_NAME_DEFAULT, sample_rate_resample


def preprocessAudioStandalone(audio: torch.tensor) -> torch.tensor:
    """
    Preprocess the audio by normalizing it.

    Args:
        audio (torch.tensor): The input audio tensor.

    Returns:
        torch.tensor: The normalized audio tensor.
    """
    audio = audio-torch.mean(audio)
    audio = audio/torch.max(torch.abs(audio))
    return audio


class PronunciationTrainer:
    """
    A class to train and evaluate pronunciation accuracy using ASR and phoneme conversion models.
    """
    current_transcript: str
    current_ipa: str

    current_recorded_audio: torch.Tensor
    current_recorded_transcript: str
    current_recorded_word_locations: list
    current_recorded_intonations: torch.tensor
    current_words_pronunciation_accuracy = []
    categories_thresholds = np.array([80, 60, 59])

    sampling_rate = sample_rate_resample

    def __init__(self, asr_model: mi.IASRModel, word_to_ipa_coverter: mi.ITextToPhonemModel) -> None:
        """
        Initialize the PronunciationTrainer with ASR and phoneme conversion models.

        Args:
            asr_model (mi.IASRModel): The ASR model to use.
            word_to_ipa_coverter (mi.ITextToPhonemModel): The phoneme conversion model to use.
        """
        self.asr_model = asr_model
        self.ipa_converter = word_to_ipa_coverter

    def getTranscriptAndWordsLocations(self, audio_length_in_samples: int) -> tuple[str, list]:
        """
        Get the transcript and word locations from the ASR model.

        Args:
            audio_length_in_samples (int): The length of the audio in samples.

        Returns:
            tuple: A tuple containing the audio transcript and word locations in samples.
        """
        audio_transcript = self.asr_model.getTranscript()
        word_locations_in_samples = self.asr_model.getWordLocations()

        fade_duration_in_samples = 0.05*self.sampling_rate
        word_locations_in_samples = [(int(np.maximum(0, word['start_ts']-fade_duration_in_samples)), int(np.minimum(
            audio_length_in_samples-1, word['end_ts']+fade_duration_in_samples))) for word in word_locations_in_samples]

        return audio_transcript, word_locations_in_samples

    # def getWordsRelativeIntonation(self, Audio: torch.tensor, word_locations: list):
    #     intonations = torch.zeros((len(word_locations), 1))
    #     intonation_fade_samples = 0.3*self.sampling_rate
    #     app_logger.info(f"intonations.shape: {intonations.shape}.")
    #     for word in range(len(word_locations)):
    #         intonation_start = int(np.maximum(
    #             0, word_locations[word][0]-intonation_fade_samples))
    #         intonation_end = int(np.minimum(
    #             Audio.shape[1]-1, word_locations[word][1]+intonation_fade_samples))
    #         intonations[word] = torch.sqrt(torch.mean(
    #             Audio[0][intonation_start:intonation_end]**2))
    #
    #     intonations = intonations/torch.mean(intonations)
    #     return intonations

    ##################### ASR Functions ###########################

    def processAudioForGivenText(self, recordedAudio: torch.Tensor = None, real_text=None) -> dict:
        """
        Process the recorded audio and evaluate pronunciation accuracy.

        Args:
            recordedAudio (torch.Tensor, optional): The recorded audio tensor. Defaults to None.
            real_text (str, optional): The real text to compare against. Defaults to None.

        Returns:
            dict: A dictionary containing the evaluation results.
        """
        start = time.time()
        recording_transcript, recording_ipa, word_locations = self.getAudioTranscript(
            recordedAudio)
        time_transcript_audio = time.time() - start
        app_logger.info(f'Time for NN to transcript audio: {time_transcript_audio:.2f}.')

        start = time.time()
        real_and_transcribed_words, real_and_transcribed_words_ipa, mapped_words_indices = self.matchSampleAndRecordedWords(
            real_text, recording_transcript)
        time_matching_transcripts = time.time() - start
        app_logger.info(f'Time for matching transcripts: {time_matching_transcripts:.3f}.')

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

    def getAudioTranscript(self, recordedAudio: torch.Tensor = None) -> tuple[str | list]:
        """
        Get the transcript and IPA representation of the recorded audio.

        Args:
            recordedAudio (torch.Tensor, optional): The recorded audio tensor. Defaults to None.

        Returns:
            tuple: A tuple containing the transcript, IPA representation, and word locations.
        """
        current_recorded_audio = recordedAudio

        current_recorded_audio = self.preprocessAudio(
            current_recorded_audio)
        self.asr_model.processAudio(current_recorded_audio)

        current_recorded_transcript, current_recorded_word_locations = self.getTranscriptAndWordsLocations(
            current_recorded_audio.shape[1])
        current_recorded_ipa = self.ipa_converter.convertToPhonem(
            current_recorded_transcript)

        # time.sleep(10000)
        return current_recorded_transcript, current_recorded_ipa, current_recorded_word_locations

    def getWordLocationsFromRecordInSeconds(self, word_locations, mapped_words_indices) -> list:
        """
        Get the start and end times of words in the recorded audio in seconds.

        Args:
            word_locations (list): The word locations in samples.
            mapped_words_indices (list): The indices of the mapped words.

        Returns:
            list: A list containing the start and end times of words in seconds.
        """
        app_logger.info(f"len_list: word_locations:{len(word_locations)},  mapped_words_indices:{len(mapped_words_indices)}, {len(word_locations) == len(mapped_words_indices)}...")
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
        """
        Match the real text with the recorded transcript and get the IPA representations.

        Args:
            real_text (str): The real text to compare against.
            recorded_transcript (str): The recorded transcript.

        Returns:
            tuple: A tuple containing the matched words, IPA representations, and mapped word indices.
        """
        words_estimated = recorded_transcript.split()

        try:
            words_real = real_text.split()
        except AttributeError:
            raise ValueError("Real text is None, but should be a string.")

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

    def getPronunciationAccuracy(self, real_and_transcribed_words_ipa) -> float:
        """
        Calculate the pronunciation accuracy based on the IPA representations.

        Args:
            real_and_transcribed_words_ipa (list): A list of tuples containing the real and transcribed IPA representations.

        Returns:
            float: The percentage of correct pronunciations.
        """
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
        """
        Remove punctuation from a word.

        Args:
            word (str): The input word.

        Returns:
            str: The word without punctuation.
        """
        return ''.join([char for char in word if char not in punctuation])

    def getWordsPronunciationCategory(self, accuracies) -> list:
        """
        Get the pronunciation category for each word based on accuracy.

        Args:
            accuracies (list): A list of pronunciation accuracies.

        Returns:
            list: A list of pronunciation categories.
        """
        categories = []

        for accuracy in accuracies:
            categories.append(
                self.getPronunciationCategoryFromAccuracy(accuracy))

        return categories

    def getPronunciationCategoryFromAccuracy(self, accuracy) -> int:
        """
        Get the pronunciation category based on accuracy.

        Args:
            accuracy (float): The pronunciation accuracy.

        Returns:
            int: The pronunciation category.
        """
        return np.argmin(abs(self.categories_thresholds-accuracy))

    def preprocessAudio(self, audio: torch.tensor) -> torch.tensor:
        """
        Preprocess the audio by normalizing it.

        Args:
            audio (torch.tensor): The input audio tensor.

        Returns:
            torch.tensor: The normalized audio tensor.
        """
        return preprocessAudioStandalone(audio)


def getTrainer(language: str, model_name: str = MODEL_NAME_DEFAULT) -> PronunciationTrainer:
    """
    Get a PronunciationTrainer instance for the specified language and model.

    Args:
        language (str): The language of the model.
        model_name (str, optional): The name of the model. Defaults to MODEL_NAME_DEFAULT.

    Returns:
        PronunciationTrainer: An instance of PronunciationTrainer.
    """
    asr_model = mo.getASRModel(language, model_name=model_name)
    if language == 'de':
        phonem_converter = RuleBasedModels.EpitranPhonemConverter(epitran.Epitran('deu-Latn'))
    elif language == 'en':
        phonem_converter = RuleBasedModels.EngPhonemConverter()
    else:
        raise ValueError(f"Language '{language}' not implemented")
    trainer = PronunciationTrainer(asr_model, phonem_converter)

    return trainer
