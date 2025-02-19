import torch
import torch.nn as nn

from AIModels import NeuralASR
from ModelInterfaces import IASRModel
from constants import MODEL_NAME_DEFAULT, language_not_implemented


def getASRModel(language: str, model_name: str = MODEL_NAME_DEFAULT) -> IASRModel:
    models_dict = {
        "whisper": __get_model_whisper,
        "faster_whisper": __get_model_faster_whisper,
        "silero": __get_model_silero
    }
    if model_name in models_dict:
        fn = models_dict[model_name]
        return fn(language)
    models_supported = ", ".join(models_dict.keys())
    raise ValueError(f"Model '{model_name}' not implemented. Supported models: {models_supported}.")


def __get_model_whisper(language: str) -> IASRModel:
    from whisper_wrapper import WhisperASRModel
    return WhisperASRModel(language=language)


def __get_model_faster_whisper(language: str) -> IASRModel:
    from faster_whisper_wrapper import FasterWhisperASRModel
    return FasterWhisperASRModel(language=language)


def __get_model_silero(language: str) -> IASRModel:
    if language not in ['de', 'en']:
        raise ValueError(language_not_implemented.format(language))
    model, decoder, utils = torch.hub.load(
        repo_or_dir='snakers4/silero-models',
        model='silero_stt',
        language=language,
        device=torch.device('cpu')
    )
    model.eval()
    return NeuralASR(model, decoder)


def getTTSModel(language: str) -> nn.Module:
    if language == 'de':
        speaker = 'thorsten_v2'  # 16 kHz
        model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                  model='silero_tts',
                                  language=language,
                                  speaker=speaker)
    elif language == 'en':
        speaker = 'lj_16khz'  # 16 kHz
        model, _, _, _, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                               model='silero_tts',
                               language=language,
                               speaker=speaker)
    else:
        raise ValueError(language_not_implemented.format(language))

    return model


def getTranslationModel(language: str) -> nn.Module:
    from transformers import AutoTokenizer
    from transformers import AutoModelForSeq2SeqLM
    if language == 'de':
        model = AutoModelForSeq2SeqLM.from_pretrained(
            "Helsinki-NLP/opus-mt-de-en")
        tokenizer = AutoTokenizer.from_pretrained(
            "Helsinki-NLP/opus-mt-de-en")
        # Cache models to avoid Hugging face processing (not needed now)
        # with open('translation_model_de.pickle', 'wb') as handle:
        #     pickle.dump(model, handle)
        # with open('translation_tokenizer_de.pickle', 'wb') as handle:
        #     pickle.dump(tokenizer, handle)
    else:
        raise ValueError(language_not_implemented.format(language))

    return model, tokenizer
