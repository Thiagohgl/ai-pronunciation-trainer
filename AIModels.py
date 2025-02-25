import numpy as np
import torch
import ModelInterfaces


class NeuralASR(ModelInterfaces.IASRModel):
    word_locations_in_samples = None
    audio_transcript = None

    def __init__(self, model: torch.nn.Module, decoder) -> None:
        """
        Initialize the NeuralASR (Audio Speech Recognition) model.

        Args:
            model (torch.nn.Module): The neural network model for ASR.
            decoder: The decoder to convert CTC outputs to transcripts.
        """
        super().__init__()
        self.model = model
        self.decoder = decoder  # Decoder from CTC-outputs to transcripts

    def getTranscript(self) -> str:
        """
        Get the transcript of the processed audio.

        Returns:
            str: The audio transcript.

        Raises:
            AssertionError: If the audio has not been processed.
        """
        assert self.audio_transcript is not None, 'Can get audio transcripts without having processed the audio'
        return self.audio_transcript

    def getWordLocations(self) -> list:
        """
        Get the word locations from the processed audio.

        Returns:
            list: A list of word locations in samples.

        Raises:
            AssertionError: If the audio has not been processed.
        """
        assert self.word_locations_in_samples is not None, 'Can get word locations without having processed the audio'
        return self.word_locations_in_samples

    def processAudio(self, audio: torch.Tensor) -> None:
        """
        Process the audio to generate transcripts and word locations.

        Args:
            audio (torch.Tensor): The input audio tensor.
        """
        audio_length_in_samples = audio.shape[1]
        with torch.inference_mode():
            nn_output = self.model(audio)

            self.audio_transcript, self.word_locations_in_samples = self.decoder(
                nn_output[0, :, :].detach(), audio_length_in_samples, word_align=True)


class NeuralTTS(ModelInterfaces.ITextToSpeechModel):
    def __init__(self, model: torch.nn.Module, sampling_rate: int) -> None:
        """
        Initialize the NeuralTTS (Text to Speech) model.

        Args:
            model (torch.nn.Module): The neural network model for TTS.
            sampling_rate (int): The sampling rate for the audio.
        """
        super().__init__()
        self.model = model
        self.sampling_rate = sampling_rate

    def getAudioFromSentence(self, sentence: str) -> np.array:
        """
        Generate audio from a given sentence.

        Args:
            sentence (str): The input sentence.

        Returns:
            np.array: The generated audio as a numpy array.
        """
        with torch.inference_mode():
            audio_transcript = self.model.apply_tts(texts=[sentence],
                                                    sample_rate=self.sampling_rate)[0]

        return audio_transcript


class NeuralTranslator(ModelInterfaces.ITranslationModel):
    def __init__(self, model: torch.nn.Module, tokenizer) -> None:
        """
        Initialize the NeuralTranslator model.

        Args:
            model (torch.nn.Module): The neural network model for translation.
            tokenizer: The tokenizer for text processing.
        """
        super().__init__()
        self.model = model
        self.tokenizer = tokenizer

    def translateSentence(self, sentence: str) -> str:
        """
        Translate a given sentence to the target language.

        Args:
            sentence (str): The input sentence.

        Returns:
            str: The translated sentence.
        """
        tokenized_text = self.tokenizer(sentence, return_tensors='pt')
        translation = self.model.generate(**tokenized_text)
        translated_text = self.tokenizer.batch_decode(
            translation, skip_special_tokens=True)[0]

        return translated_text
