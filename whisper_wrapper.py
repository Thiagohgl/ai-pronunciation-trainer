from typing import Union

import numpy as np
import torch
import whisper

from ModelInterfaces import IASRModel
from constants import sample_rate_resample, app_logger


def parse_word_info(word_info: dict, sample_rate: int) -> dict:
    """Parse a word info object from WhisperModel into a dictionary with start and end timestamps.

    Args:
        word_info (dict): Word dictionary object
    """
    word = word_info["word"]
    start_ts = float(word_info["start"]) * sample_rate
    end_ts = float(word_info["end"]) * sample_rate
    return {"word": word, "start_ts": start_ts, "end_ts": end_ts}


class WhisperASRModel(IASRModel):
    """Whisper ASR model wrapper class. This class is used to transcribe audio and store the transcript and word locations."""
    def __init__(self, model_name="base", language=None):
        self.asr = whisper.load_model(model_name)
        self._transcript = ""
        self._word_locations = []
        self.sample_rate = sample_rate_resample
        self.language = language

    def processAudio(self, audio:Union[np.ndarray, torch.Tensor]):
        """Transcribe audio and store the transcript and word locations updating self._transcript and self._word_locations,
        get these values using getTranscript() and getWordLocations() respectively.

        Args:
            audio (np.ndarray or torch.Tensor): Audio samples to transcribe.

        Returns:
            None
        """
        # 'audio' can be a path to a file or a numpy array of audio samples.
        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()
        result = self.asr.transcribe(audio=audio[0], **{"language": self.language, "fp16": True, "task": "transcribe", "word_timestamps": True})  #, "verbose": True})
        app_logger.info(f"result: type={type(result)} #")
        app_logger.debug(f"result: {result} #")
        self._transcript = result["text"]
        segments = result["segments"]
        len_segments = len(segments)
        app_logger.info(f"segments: type={type(segments)}, len:{len_segments} #")
        for segment in segments:
            words = segment["words"]
            segment_word_locations = [parse_word_info(word_info, sample_rate=self.sample_rate) for word_info in words]
            self._word_locations.extend(segment_word_locations)
            app_logger.info(f"elaborated segment {segment['id']}/{len_segments-1}: type={type(segment)}, len(words):{len(words)}, text:{segment['text']} #")

    def getTranscript(self) -> str:
        """Get the transcript of the audio."""
        return self._transcript

    def getWordLocations(self) -> list[dict]:
        """Get the word locations of the audio."""
        return self._word_locations
