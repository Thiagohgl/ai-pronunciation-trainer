import os
from pathlib import Path
import structlog
import session_logger


PROJECT_ROOT_FOLDER = Path(__file__).parent
ALLOWED_ORIGIN = os.getenv('ALLOWED_ORIGIN', 'http://localhost:3000')
LOG_JSON_FORMAT = bool(os.getenv("LOG_JSON_FORMAT"))
log_level = os.getenv("LOG_LEVEL", "INFO")
session_logger.setup_logging(json_logs=LOG_JSON_FORMAT, log_level=log_level)
app_logger = structlog.stdlib.get_logger(__name__)
sample_rate_start = int(os.getenv('SAMPLE_RATE', 48000))
sample_rate_resample = 16000
