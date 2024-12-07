import os
from pathlib import Path

import structlog
from dotenv import load_dotenv

from aip_trainer.utils import session_logger


load_dotenv()
PROJECT_ROOT_FOLDER = Path(globals().get("__file__", "./_")).absolute().parent.parent
LOG_JSON_FORMAT = bool(os.getenv("LOG_JSON_FORMAT"))
log_level = os.getenv("LOG_LEVEL", "INFO")
sample_rate_start = int(os.getenv('SAMPLE_RATE', 48000))
accepted_sample_rates = [48000, 24000, 16000, 8000]
try:
    assert sample_rate_start in accepted_sample_rates
except AssertionError:
    raise ValueError(f"cannot use a sample rate of value '{sample_rate_start}', should be one of {accepted_sample_rates} ...")
session_logger.setup_logging(json_logs=LOG_JSON_FORMAT, log_level=log_level)
app_logger = structlog.stdlib.get_logger(__name__)
