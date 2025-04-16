import torch 
from transformers import pipeline
from ModelInterfaces import IASRModel
from typing import Union
import numpy as np 

class WhisperASRModel(IASRModel):
    def __init__(self, model_name="openai/whisper-large"):
        self.asr = pipeline("automatic-speech-recognition", model=model_name, return_timestamps="word")
        self._transcript = ""
        self._word_locations = []
        self.sample_rate = 16000

    def processAudio(self, audio:Union[np.ndarray, torch.Tensor], lang="en"):
        # 'audio' can be a path to a file or a numpy array of audio samples.
        if isinstance(audio, torch.Tensor):
            audio = audio.detach().cpu().numpy()
        result = self.asr(audio[0], generate_kwargs={"language": "<|" + lang + "|>"})
        self._transcript = result["text"]

        print("---------------->result: ", result)
        self._word_locations = [{"word":word_info["text"], "start_ts":word_info["timestamp"][0]*self.sample_rate,
                                 "end_ts":word_info["timestamp"][1]*self.sample_rate} for word_info in result["chunks"]]

    def getTranscript(self) -> str:
        return self._transcript

    def getWordLocations(self) -> list:
        
        return self._word_locations
    
if __name__ == "__main__":
    import torchaudio
    model = WhisperASRModel()


    wav, sr = torchaudio.load("short_sample.wav")
    input = wav[0].numpy()
    model.processAudio([input])
    print(model.getTranscript())
    print(model.getWordLocations())  # This will print the word locations in the audio file.
