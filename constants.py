import os
from pathlib import Path
import structlog
import session_logger

PROJECT_ROOT_FOLDER = Path(__file__).parent
ALLOWED_ORIGIN = os.getenv('ALLOWED_ORIGIN', 'http://localhost:3000')
LOG_JSON_FORMAT = bool(os.getenv("LOG_JSON_FORMAT"))
IS_TESTING = bool(os.getenv('IS_TESTING', ""))
STSCOREAPIKEY = os.getenv('STSCOREAPIKEY', "stscore_apikey_placeholder")
log_level = os.getenv("LOG_LEVEL", "INFO")
USE_DTW = bool(os.getenv("USE_DTW"))
MODEL_NAME_TESTING = "whisper"
_MODEL_NAME_DEFAULT = os.getenv("MODEL_NAME_DEFAULT", MODEL_NAME_TESTING)
MODEL_NAME_DEFAULT = MODEL_NAME_TESTING if IS_TESTING else _MODEL_NAME_DEFAULT
DEVICE = os.getenv("DEVICE", "cpu")
tmp_audio_extension = os.getenv('TMP_AUDIO_EXTENSION', '.wav')
session_logger.setup_logging(json_logs=LOG_JSON_FORMAT, log_level=log_level)
app_logger = structlog.stdlib.get_logger(__name__)
sample_rate_start = int(os.getenv('SAMPLE_RATE', 48000))
sample_rate_resample = 16000
samplerate_tts = 16000
language_not_implemented = "Language '{}' not implemented. Supported languages: 'de', 'en'."
SILERO_VERSION_DE = "v4"
SILERO_VERSION_EN = "latest"
silero_versions_dict = {"de": SILERO_VERSION_DE, "en": SILERO_VERSION_EN}
model_urls = {
    "faster_whisper": "https://pypi.org/project/faster-whisper/",
    "silero": "https://pypi.org/project/silero/",
    "whisper": "https://pypi.org/project/openai-whisper/",
}