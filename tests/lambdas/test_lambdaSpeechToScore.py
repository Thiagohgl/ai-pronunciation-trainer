import json
import os
import platform
import unittest
## permit to import from parent directory also in
# import sys
# from pathlib import Path
# parent = Path(__file__).parent.parent.parent
# sys.path.append(str(parent))
# print(f"## sys.path:{sys.path}.")

import lambdaSpeechToScore
from constants import ALLOWED_ORIGIN, app_logger
from tests import EVENTS_FOLDER, set_seed
from tests.lambdas.constants_lambdaSpeechToScore import expected_GetAccuracyFromRecordedAudio


def helper_get_accuracy_from_recorded_audio(cls, expected_output, source, use_dtw):
    with open(EVENTS_FOLDER / "GetAccuracyFromRecordedAudio.json", "r") as src:
        inputs_outputs = json.load(src)
    inputs = inputs_outputs["inputs"]
    for language, event_content in inputs.items():
        set_seed()
        current_expected_output_source = expected_output[source]
        dtw = f"dtw_{use_dtw}".lower()
        current_expected_output_dtw_true = current_expected_output_source[dtw]
        current_expected_output = current_expected_output_dtw_true[language]
        event_content_loaded = json.loads(event_content["body"])
        event_content_loaded["useDTW"] = use_dtw
        event_content["body"] = json.dumps(event_content_loaded)
        output = lambdaSpeechToScore.lambda_handler(event_content, {})
        output = json.loads(output)
        app_logger.info(
            f"output type:{type(output)}, expected_output type:{type(current_expected_output)}."
        )
        try:
            cls.assertDictEqual(output, current_expected_output)
        except Exception as ex:
            app_logger.error(f"# output, source:{source}, use_dtw:{use_dtw}, language:{language}.")
            app_logger.error(output)
            app_logger.error(f"ex.args:{ex.args} .")
            app_logger.error(f"ex:{ex} .")
            raise ex


class TestGetAccuracyFromRecordedAudio(unittest.TestCase):
    def setUp(self):
        if platform.system() == "Windows" or platform.system() == "Win32":
            os.environ["PYTHONUTF8"] = "1"
            os.environ["IS_TESTING"] = "TRUE"

    def tearDown(self):
        if platform.system() == "Windows" or platform.system() == "Win32" and "PYTHONUTF8" in os.environ:
            del os.environ["PYTHONUTF8"]
            del os.environ["IS_TESTING"]

    def test_GetAccuracyFromRecordedAudio_false(self):
        self.maxDiff = None
        try:
            helper_get_accuracy_from_recorded_audio(self, expected_GetAccuracyFromRecordedAudio, "cmd", False)
        except AssertionError:
            helper_get_accuracy_from_recorded_audio(self, expected_GetAccuracyFromRecordedAudio, "gui", False)

    def test_GetAccuracyFromRecordedAudio_true(self):
        self.maxDiff = None
        try:
            helper_get_accuracy_from_recorded_audio(self, expected_GetAccuracyFromRecordedAudio, "cmd", True)
        except AssertionError:
            helper_get_accuracy_from_recorded_audio(self, expected_GetAccuracyFromRecordedAudio, "gui", True)

    def test_lambda_handler_empty_text(self):
        with open(EVENTS_FOLDER / "GetAccuracyFromRecordedAudio.json", "r") as src:
            inputs_outputs = json.load(src)
        event = inputs_outputs["inputs"]["en"]
        event_body = event["body"]
        event_body_loaded = json.loads(event_body)
        event_body_loaded["title"] = ""
        event_body = json.dumps(event_body_loaded)
        event["body"] = event_body
        output = lambdaSpeechToScore.lambda_handler(event, {})
        self.assertDictEqual(
            output,
            {
                "statusCode": 200,
                'headers': {
                    'Access-Control-Allow-Headers': ALLOWED_ORIGIN,
                    'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
                    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
                },
                "body": "",
            },
        )


if __name__ == "__main__":
    unittest.main()
