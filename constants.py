import os
from pathlib import Path


PROJECT_ROOT_FOLDER = Path(__file__).parent
ALLOWED_ORIGIN = os.getenv('ALLOWED_ORIGIN', 'http://localhost:3000')
LOG_JSON_FORMAT = bool(os.getenv("LOG_JSON_FORMAT"))
IS_TESTING = os.getenv('IS_TESTING', "")
STSCOREAPIKEY = os.getenv('STSCOREAPIKEY', "stscore_apikey_placeholder")
log_level = os.getenv("LOG_LEVEL", "INFO")
sample_rate_start = int(os.getenv('SAMPLE_RATE', 48000))
sample_rate_resample = 16000
