import torch 
from transformers import pipeline
from ModelInterfaces import IASRModel
from typing import Union
import numpy as np 

class WhisperASRModel(IASRModel):
    def __init__(self, model_name="openai/whisper-base"):
        self.asr = pipeline("automatic-speech-recognition", model=model_name, return_timestamps="word")
        self._transcript = ""
        self._word_locations = []
        self.sample_rate = 16000

    def processAudio(self, audio:Union[np.ndarray, torch.Tensor]):
        # 'audio' can be a path to a file or a numpy array of audio samples.
        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()
        size = audio.size
        shape = audio.shape
        result = self.asr(audio[0])
        print('result:', result)
        print("last", result["chunks"][-1])
        print(f"type:{type(audio)} => size:{size}, shape:{shape} #")
        self._transcript = result["text"]
        chunks = result["chunks"]
        try:
            self._word_locations = [parse_word_info(word_info, self.sample_rate, audio_shape_axis1=shape[1], is_last=n==len(chunks)-1) for n, word_info in enumerate(chunks)]
        except Exception as e:
            print(f"error, result:{result} ...")
            raise ValueError(f"processAudio::Error in parsing word info: {e} ...")
        print("transcript:", self._transcript)

    def getTranscript(self) -> str:
        return self._transcript

    def getWordLocations(self) -> list:

        return self._word_locations

def parse_word_info(word_info, sample_rate, audio_shape_axis1, is_last=False):
    try:
        text = word_info["text"]
        timestamp = word_info["timestamp"]
        start_ts, end_ts = get_timestamps(timestamp, audio_shape_axis1, sample_rate, word_info, is_last)
        data = {"word":text, "start_ts":start_ts, "end_ts":end_ts}
        print("data:", data)
        return data
    except Exception as e:
        print(f"type exception:{type(e)} ...")
        print(f"parse_word_info::error, word_info:{word_info} ...")
        raise ValueError(f"parse_word_info::Error in parsing word info: {e} ...")


def get_timestamps(timestamp, audio_shape_axis1, sample_rate, word_info, is_last=False):
    try:
        return timestamp[0]*sample_rate, timestamp[1]*sample_rate
    except (IndexError, TypeError) as ex:
        if is_last:
            return timestamp[0]*sample_rate, audio_shape_axis1
        print(f"get_timestamps, timestamp:{timestamp}.")
        print(f"get_timestamps, audio_shape_axis1:{audio_shape_axis1}.")
        print(f"get_timestamps, sample_rate:{sample_rate}.")
        print(f"get_timestamps, word_info:{word_info}.")
        print(f"get_timestamps, is_last:{is_last}.")
        print(f"get_timestamps, ex:{ex}.")
        raise ValueError(f"get_timestamps::The end timestamp is not provided for the word '{word_info}'.")
