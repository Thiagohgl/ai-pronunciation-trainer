import os

import structlog
from aip_trainer import PROJECT_ROOT_FOLDER, LOG_JSON_FORMAT
from aip_trainer.utils import session_logger


TEST_ROOT_FOLDER = PROJECT_ROOT_FOLDER / "tests"
EVENTS_FOLDER = TEST_ROOT_FOLDER / "events"
log_level = os.getenv("LOG_LEVEL", "INFO")
session_logger.setup_logging(json_logs=LOG_JSON_FORMAT, log_level=log_level)
test_logger = structlog.stdlib.get_logger(__name__)
