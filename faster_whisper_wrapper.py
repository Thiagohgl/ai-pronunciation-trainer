from typing import Union

import numpy as np
import onnxruntime
import torch
from faster_whisper import WhisperModel, transcribe

from ModelInterfaces import IASRModel
from constants import sample_rate_resample, app_logger, IS_TESTING, DEVICE
from typing_hints import ParsedWordInfo


device = onnxruntime.get_device()
device = "cpu" if IS_TESTING or device.lower() == DEVICE.lower() else device
app_logger.info(f"device: {device} #")
device_compute = "int8_float16" if device == "cuda" else "int8"
app_logger.info(f"device: {device}, device_compute: {device_compute} #")


def parse_word_info(word_info: transcribe.Word, sample_rate: int) -> ParsedWordInfo:
    """Parse a word info object from WhisperModel into a dictionary with start and end timestamps.

    Args:
        word_info (transcribe.Word): Word object from WhisperModel.transcribe module
        sample_rate (int): Sample rate of the audio

    Returns:
        ParsedWordInfo: Dictionary with the current single word, start_ts and end_ts keys
    """
    start_ts = float(word_info.start) * sample_rate
    end_ts = float(word_info.end) * sample_rate
    word = word_info.word
    return {"word": word, "start_ts": start_ts, "end_ts": end_ts}


class FasterWhisperASRModel(IASRModel):
    """Faster Whisper ASR model wrapper class. This class is used to transcribe audio and store the transcript and word locations."""
    def __init__(self, model_name:str="base", language:str=None):
        self.asr = WhisperModel(model_name, device=device, compute_type=device_compute)
        self._transcript = ""
        self._word_locations = []
        self.sample_rate = sample_rate_resample
        self.language = language

    def processAudio(self, audio:Union[np.ndarray, torch.Tensor]) -> None:
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
        segments, info = self.asr.transcribe(audio=audio[0], language=self.language, word_timestamps=True, beam_size=5, temperature=0, vad_filter=True)  #, "verbose": True})
        app_logger.debug(f"segments: type={type(segments)}, segments complete: {segments} #")
        app_logger.info(f"info: type={type(info)}, info complete: {info} #")
        transcript = []
        count = 0
        for segment in segments:
            app_logger.debug(f"single segment: {type(segment)}, segment: {segment} #")
            transcript.append(segment.text)
            segment_word_locations = [parse_word_info(word_info, sample_rate=self.sample_rate) for word_info in segment.words]
            self._word_locations.extend(segment_word_locations)
            app_logger.info(f"elaborated segment {count}: type={type(segment)}, len(words):{len(segment.words)}, text:{segment.text} #")
            count += 1
        app_logger.info(f"transcript: {transcript} #")
        self._transcript = " ".join(transcript)

    def getTranscript(self) -> str:
        """Get the transcript of the audio."""
        return self._transcript

    def getWordLocations(self) -> list[ParsedWordInfo]:
        """Get a list of ParsedWordInfo"""
        return self._word_locations
