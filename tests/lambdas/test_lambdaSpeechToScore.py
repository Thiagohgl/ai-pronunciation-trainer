import json
import os
import platform
import unittest

import lambdaSpeechToScore
from constants import ALLOWED_ORIGIN
from tests import EVENTS_FOLDER, set_seed
from tests.lambdas.constants_lambdaSpeechToScore import expected_GetAccuracyFromRecordedAudio


class TestGetAccuracyFromRecordedAudio(unittest.TestCase):
    def setUp(self):
        if platform.system() == "Windows" or platform.system() == "Win32":
            os.environ["PYTHONUTF8"] = "1"

    def tearDown(self):
        if (
            platform.system() == "Windows" or platform.system() == "Win32"
        ) and "PYTHONUTF8" in os.environ:
            del os.environ["PYTHONUTF8"]

    def test_GetAccuracyFromRecordedAudio(self):
        self.maxDiff = None
        with open(EVENTS_FOLDER / "GetAccuracyFromRecordedAudio.json", "r") as src:
            inputs_outputs = json.load(src)
        inputs = inputs_outputs["inputs"]
        for language, event_content in inputs.items():
            set_seed()
            current_expected_output = expected_GetAccuracyFromRecordedAudio[language]
            output = lambdaSpeechToScore.lambda_handler(event_content, [])
            output = json.loads(output)
            print(
                f"output type:{type(output)}, expected_output type:{type(current_expected_output)}."
            )
            try:
                self.assertDictEqual(output, current_expected_output)
            except Exception as e:
                print("output:", output, "#")
                raise e

    def test_lambda_handler_empty_text(self):
        with open(EVENTS_FOLDER / "GetAccuracyFromRecordedAudio.json", "r") as src:
            inputs_outputs = json.load(src)
        event = inputs_outputs["inputs"]["en"]
        event_body = event["body"]
        event_body_loaded = json.loads(event_body)
        event_body_loaded["title"] = ""
        event_body = json.dumps(event_body_loaded)
        event["body"] = event_body
        output = lambdaSpeechToScore.lambda_handler(event, [])
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
