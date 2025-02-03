
import torch
import numpy as np
import models as mo
import WordMetrics
import WordMatching as wm
import epitran
import ModelInterfaces as mi
import AIModels
import RuleBasedModels
from string import punctuation
import time
from constants import sample_rate_resample, app_logger


def getTrainer(language: str):

    asr_model = mo.getASRModel(language,use_whisper=True)
    
    if language == 'de':
        phonem_converter = RuleBasedModels.EpitranPhonemConverter(
            epitran.Epitran('deu-Latn'))
    elif language == 'en':
        phonem_converter = RuleBasedModels.EngPhonemConverter()
    else:
        raise ValueError('Language not implemented')

    trainer = PronunciationTrainer(
        asr_model, phonem_converter)

    return trainer


def preprocessAudioStandalone(audio: torch.tensor) -> torch.tensor:
    audio = audio-torch.mean(audio)
    audio = audio/torch.max(torch.abs(audio))
    return audio


class PronunciationTrainer:
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
        self.asr_model = asr_model
        self.ipa_converter = word_to_ipa_coverter

    def getTranscriptAndWordsLocations(self, audio_length_in_samples: int):

        audio_transcript = self.asr_model.getTranscript()
        word_locations_in_samples = self.asr_model.getWordLocations()

        fade_duration_in_samples = 0.05*self.sampling_rate
        word_locations_in_samples = [(int(np.maximum(0, word['start_ts']-fade_duration_in_samples)), int(np.minimum(
            audio_length_in_samples-1, word['end_ts']+fade_duration_in_samples))) for word in word_locations_in_samples]

        return audio_transcript, word_locations_in_samples

    def getWordsRelativeIntonation(self, Audio: torch.tensor, word_locations: list):
        intonations = torch.zeros((len(word_locations), 1))
        intonation_fade_samples = 0.3*self.sampling_rate
        app_logger.info(f"intonations.shape: {intonations.shape}.")
        for word in range(len(word_locations)):
            intonation_start = int(np.maximum(
                0, word_locations[word][0]-intonation_fade_samples))
            intonation_end = int(np.minimum(
                Audio.shape[1]-1, word_locations[word][1]+intonation_fade_samples))
            intonations[word] = torch.sqrt(torch.mean(
                Audio[0][intonation_start:intonation_end]**2))

        intonations = intonations/torch.mean(intonations)
        return intonations

    ##################### ASR Functions ###########################

    def processAudioForGivenText(self, recordedAudio: torch.Tensor = None, real_text=None):

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

    def getAudioTranscript(self, recordedAudio: torch.Tensor = None):
        current_recorded_audio = recordedAudio

        current_recorded_audio = self.preprocessAudio(
            current_recorded_audio)

        self.asr_model.processAudio(current_recorded_audio)

        current_recorded_transcript, current_recorded_word_locations = self.getTranscriptAndWordsLocations(
            current_recorded_audio.shape[1])
        current_recorded_ipa = self.ipa_converter.convertToPhonem(
            current_recorded_transcript)

        return current_recorded_transcript, current_recorded_ipa, current_recorded_word_locations

    def getWordLocationsFromRecordInSeconds(self, word_locations, mapped_words_indices) -> list:
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

    def getPronunciationAccuracy(self, real_and_transcribed_words_ipa) -> float:
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
        return preprocessAudioStandalone(audio)


def log_errors(s, name, caller):
    app_logger.error(f"args => caller:{caller}, {name}: {len(s)}, {s} ...")
