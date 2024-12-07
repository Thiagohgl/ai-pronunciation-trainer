import random
import tempfile
from pathlib import Path

from aip_trainer import app_logger


def get_tts(text: str, language: str, tmp_prefix="audio_", tmp_suffix=".wav") -> str:
    """
    Generate text-to-speech (TTS) audio for the given text and language.

    Args:
        text (str): The text to be converted to speech.
        language (str): The language of the text. Supported languages are "en" (English) and "de" (German).
        tmp_prefix (str, optional): The temporary directory to use for temporary files.
        tmp_suffix (str, optional): The temporary directory to use for temporary files.

    Returns:
        str: The path to the generated audio file.

    Raises:
        NotImplementedError: If the provided language is not supported.

    Notes:
        This function uses the Silero TTS model to generate the audio. The model and speaker are selected based on the provided language.
    """
    from aip_trainer.models import models

    if text is None or len(text) == 0:
        raise ValueError(f"cannot read an empty/None text: '{text}'...")
    if language is None or len(language) == 0:
        raise NotImplementedError(f"Not tested/supported with '{language}' language...")

    tmp_dir = Path(tempfile.gettempdir())
    try:
        model, _, speaker, sample_rate = models.silero_tts(
            language, output_folder=tmp_dir
        )
    except ValueError:
        model, _, sample_rate, _, _, speaker = models.silero_tts(
            language, output_folder=tmp_dir
        )
    app_logger.info(f"model speaker #0: {speaker} ...")

    with tempfile.NamedTemporaryFile(prefix=tmp_prefix, suffix=tmp_suffix, delete=False) as tmp_audio_file:
        app_logger.info(f"tmp_audio_file output: {tmp_audio_file.name} ...")
        audio_paths = model.save_wav(text=text, speaker=speaker, sample_rate=sample_rate, audio_path=str(tmp_audio_file.name))
        app_logger.info(f"audio_paths output: {audio_paths} ...")
        return audio_paths
