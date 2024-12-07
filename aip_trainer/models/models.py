import os
from pathlib import Path
import tempfile
from typing import Union, Callable

import torch
import torch.nn as nn
from omegaconf import DictConfig, ListConfig
from silero.utils import Decoder

from aip_trainer import app_logger, sample_rate_start


default_speaker_dict = {
    "de": {"speaker": "karlsson", "model_id": "v3_de", "sample_rate": sample_rate_start},
    "en": {"speaker": "en_0", "model_id": "v3_en", "sample_rate": sample_rate_start},
}


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


def silero_stt(
        language: str = "en",
        version: str = "latest",
        jit_model: str = "jit",
        output_folder: Path | str = None,
        **kwargs,
    ) -> tuple[nn.Module, Decoder, set[Callable, Callable, Callable, Callable]]:
    """
    Modified function to create instances of Silero Speech-To-Text Model(s).
    Please see https://github.com/snakers4/silero-models?tab=readme-ov-file#speech-to-text for usage examples.

    Args:
        language (str): Language of the model. Available options are ['en', 'de', 'es'].
        version (str): Version of the model to use. Default is "latest".
        jit_model (str): Type of JIT model to use. Default is "jit".
        output_folder (Path | str, optional): Output folder needed in case of docker build. Default is None.
        **kwargs: Additional keyword arguments.

    Returns:
        tuple: A tuple containing the model, decoder object, and a set of utility functions.
    """
    from silero.utils import (
        read_audio,
        read_batch,
        split_into_batches,
        prepare_model_input,
    )

    model, decoder = get_latest_stt_model(
        language,
        output_folder,
        version,
        model_type="stt_models",
        jit_model=jit_model,
        **kwargs,
    )
    utils = (read_batch, split_into_batches, read_audio, prepare_model_input)

    return model, decoder, utils


def init_jit_model(
        model_url: str,
        device: torch.device = torch.device("cpu"),
        output_folder: Path | str = None,
    ) -> tuple[torch.nn.Module, Decoder]:
    """
    Initialize a JIT model from a given URL.

    Args:
        model_url (str): The URL to download the model from.
        device (torch.device, optional): The device to load the model on. Defaults to CPU.
        output_folder (Path | str, optional): The folder to save the downloaded model.
            If None, defaults to a 'model' directory in the current file's directory.

    Returns:
        Tuple[torch.jit.ScriptModule, Decoder]: The loaded JIT model and its corresponding decoder.
    """
    torch.set_grad_enabled(False)

    app_logger.info(
        f"model output_folder exists? '{output_folder is None}' => '{output_folder}' ..."
    )
    model_dir = (
        Path(output_folder)
        if output_folder is not None
        else Path(torch.hub.get_dir())
    )
    os.makedirs(model_dir, exist_ok=True)
    app_logger.info(f"downloading the models to model_dir: '{model_dir}' ...")
    model_path = model_dir / os.path.basename(model_url)
    app_logger.info(
        f"model_path exists? '{os.path.isfile(model_path)}' => '{model_path}' ..."
    )

    if not os.path.isfile(model_path):
        app_logger.info(f"downloading model_path: '{model_path}' ...")
        torch.hub.download_url_to_file(model_url, model_path, progress=True)
    app_logger.info(f"model_path {model_path} downloaded!")
    model = torch.jit.load(model_path, map_location=device)
    model.eval()
    return model, Decoder(model.labels)


# second returned type here is the custom class src.silero.utils.Decoder from snakers4/silero-models
def getASRModel(language: str) -> tuple[nn.Module, Decoder]:
    """
    Retrieve an Automatic Speech Recognition (ASR) model and its corresponding decoder
    for the specified language.

    Args:
        language (str): The language code for which the ASR model is required.
                        Supported values are "de" for German and "en" for English.

    Returns:
        tuple[nn.Module, Decoder]: A tuple containing the ASR model and its decoder.

    Raises:
        NotImplementedError: If the specified language is not supported.
    """
    tmp_dir = tempfile.gettempdir()
    if language == "de":
        model, decoder, _ = silero_stt(
            language="de", version="v4", jit_model="jit_large", output_folder=tmp_dir
        )
    elif language == "en":
        model, decoder, _ = silero_stt(language="en", output_folder=tmp_dir)
    else:
        raise NotImplementedError(
            "currenty works only for 'de' and 'en' languages, not for '{}'.".format(
                language
            )
        )

    return model, decoder


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
            models_list_file,
            progress=False,
        )
    assert os.path.exists(models_list_file)
    return OmegaConf.load(models_list_file)


def get_latest_stt_model(language: str, output_folder: str | Path, version: str, model_type: str, jit_model: str, **kwargs) -> tuple[nn.Module, Decoder]:
    """
    Retrieve the latest Speech-to-Text (STT) model for a given language and model type.

    Args:
        language (str): The language for which the STT model is required.
        output_folder (str): The directory where the model will be saved.
        version (str): The version of the model to retrieve.
        model_type (str): The type of the model (e.g., 'large', 'small').
        jit_model (str): The specific JIT model to use.
        **kwargs: Additional keyword arguments to pass to the model initialization function.

    Returns:
        tuple: A tuple containing the model and the decoder.

    Raises:
        AssertionError: If the specified language is not available in the model type.
    """
    models = get_models(language, output_folder, version, model_type)
    available_languages = list(models[model_type].keys())
    assert language in available_languages

    model, decoder = init_jit_model(
        model_url=models[model_type].get(language).get(version).get(jit_model),
        output_folder=output_folder,
        **kwargs,
    )
    return model, decoder


get_latest_model = get_latest_stt_model
