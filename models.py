import os
from pathlib import Path
from typing import Union, Callable

import torch
import torch.nn as nn
from omegaconf import DictConfig, ListConfig

from AIModels import NeuralASR
from ModelInterfaces import IASRModel
from constants import MODEL_NAME_DEFAULT, language_not_implemented, app_logger, samplerate_tts, sample_rate_start


default_speaker_dict = {
    "de": {"speaker": "karlsson", "model_id": "v3_de", "sample_rate": sample_rate_start},
    "en": {"speaker": "en_0", "model_id": "v3_en", "sample_rate": sample_rate_start},
}


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


def silero_tts(language: str = "en", version: str = "latest", output_folder: Path | str = None, **kwargs) -> tuple[nn.Module, str, int, str, dict, Callable, str]:
    """
    Modified function to create instances of Silero Text-To-Speech Models.
    Please see https://github.com/snakers4/silero-models?tab=readme-ov-file#text-to-speech for usage examples.
    language="en", version="latest", output_folder: Path | str = None, **kwargs

    Args:
        language (str): Language of the model. Available options are ['ru', 'en', 'de', 'es', 'fr']. Default is 'en'.
        version (str): Version of the model to use. Default is 'latest'.
        output_folder (Path | str): Path to the folder where the model will be saved. Default is None.
        **kwargs: Additional keyword arguments.
    Returns:
        tuple: Depending on the model version and the input arguments, returns a tuple containing:
            - model: The loaded TTS model.
            - symbols (str): The set of symbols used by the model (only for older model versions).
            - sample_rate (int): The sample rate of the model.
            - example_text (str): Example text for the model.
            - speaker (dict):
            - apply_tts (function): Function to apply TTS (only for older model versions).
            - model_id (str): The model ID (only for older model versions).

    Raises:
        AssertionError: If the specified language is not in the supported list.
    """
    output_folder = Path(output_folder)
    current_model_lang = default_speaker_dict[language]
    app_logger.info(f"model speaker current_model_lang: {current_model_lang} ...")
    if language in default_speaker_dict:
        model_id = current_model_lang["model_id"]

    models = get_models(language, output_folder, version, model_type="tts_models")
    available_languages = list(models.tts_models.keys())
    assert (
            language in available_languages
    ), f"Language not in the supported list {available_languages}"

    tts_models_lang = models.tts_models[language]
    model_conf = tts_models_lang[model_id]
    model_conf_latest = model_conf[version]
    app_logger.info(f"model_conf: {model_conf_latest} ...")
    if "_v2" in model_id or "_v3" in model_id or "v3_" in model_id or "v4_" in model_id:
        from torch import package

        model_url = model_conf_latest.package
        model_dir = output_folder / "model"
        os.makedirs(model_dir, exist_ok=True)
        model_path = output_folder / os.path.basename(model_url)
        if not os.path.isfile(model_path):
            torch.hub.download_url_to_file(model_url, model_path, progress=True)
        imp = package.PackageImporter(model_path)
        model = imp.load_pickle("tts_models", "model")
        app_logger.info(
            f"current model_conf_latest.sample_rate:{model_conf_latest.sample_rate} ..."
        )
        sample_rate = current_model_lang["sample_rate"]
        return (
            model,
            model_conf_latest.example,
            current_model_lang["speaker"],
            sample_rate,
        )
    else:
        from silero.tts_utils import apply_tts, init_jit_model as init_jit_model_tts

        model = init_jit_model_tts(model_conf_latest.jit)
        symbols = model_conf_latest.tokenset
        example_text = model_conf_latest.example
        sample_rate = model_conf_latest.sample_rate
        return model, symbols, sample_rate, example_text, apply_tts, model_id



def get_models(language: str, output_folder: str | Path, version: str, model_type: str) -> Union[DictConfig, ListConfig]:
    """
    Retrieve and load the model configuration for a specified language and model type.

    Args:
        language (str): The language for which the model is required.
        output_folder (str or Path): The folder where the model configuration file should be saved
        version (str): The version of the model.
        model_type (str): The type of the model.

    Returns:
        OmegaConf: The loaded model configuration.

    Raises:
        AssertionError: If the model configuration file does not exist after attempting to download it.

    Notes:
        If the model configuration file does not exist in the specified output folder, it will be downloaded
        from a predefined URL and saved in the output folder.
    """
    from omegaconf import OmegaConf

    output_folder = (
        Path(output_folder)
        if output_folder is not None
        else Path(os.path.dirname(__file__)).parent.parent
    )
    models_list_file = output_folder / f"latest_silero_model_{language}.yml"
    if not os.path.exists(models_list_file):
        app_logger.info(
            f"model {model_type} yml for '{language}' language, '{version}' version not found, download it in folder {output_folder}..."
        )
        torch.hub.download_url_to_file(
            "https://raw.githubusercontent.com/snakers4/silero-models/master/models.yml",
            str(models_list_file),
            progress=False,
        )
    assert os.path.exists(models_list_file)
    return OmegaConf.load(models_list_file)
