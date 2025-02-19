from typing import Union

import numpy as np
import onnxruntime
import torch
from faster_whisper import WhisperModel

from ModelInterfaces import IASRModel
from constants import sample_rate_resample, app_logger, IS_TESTING


device = onnxruntime.get_device()
device = "cpu" if IS_TESTING or device in ["GPU", "cuda"] else device
device_compute = "int8_float16" if device == "cuda" else "int8"
app_logger.info(f"device: {device}, device_compute: {device_compute} #")


def parse_word_info(word_info, sample_rate):
    start_ts = float(word_info.start) * sample_rate
    end_ts = float(word_info.end) * sample_rate
    word = word_info.word
    return {"word": word, "start_ts": start_ts, "end_ts": end_ts}


class FasterWhisperASRModel(IASRModel):
    def __init__(self, model_name="base", language=None):
        self.asr = WhisperModel(model_name, device=device, compute_type=device_compute)
        self._transcript = ""
        self._word_locations = []
        self.sample_rate = sample_rate_resample
        self.language = language

    def processAudio(self, audio:Union[np.ndarray, torch.Tensor]):
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
        return self._transcript

    def getWordLocations(self) -> list:
        return self._word_locations
