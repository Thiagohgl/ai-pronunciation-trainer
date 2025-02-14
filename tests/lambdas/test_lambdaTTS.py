import base64
import json
import os
import platform
import tempfile
import unittest
from pathlib import Path

from constants import app_logger
from lambdaSpeechToScore import audioread_load
from lambdaTTS import lambda_handler
from tests import set_seed, utilities


def helper_lambda_handler(text: str, expected_hash_output: list[bytes]):
    set_seed()
    event = {
        'body': json.dumps({'value': text})
    }
    response = lambda_handler(event, {})
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'wavBase64' in body
    b64decoded = base64.b64decode(body['wavBase64'].encode('utf-8'))
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp.write(b64decoded)
        tmp.flush()
        tmp_name = Path(tmp.name)
        audio_array, _ = audioread_load(str(tmp_name))
    tmp_name.unlink(missing_ok=True)
    hash_output = utilities.hash_calculate(audio_array, is_file=False)
    app_logger.info(f"hash_output: {hash_output}, expected_hash_output: {expected_hash_output} => {hash_output in expected_hash_output} ...")
    print(f"hash_output: {hash_output}, expected_hash_output: {expected_hash_output} => {hash_output in expected_hash_output} ...")
    try:
        assert hash_output in expected_hash_output
    except AssertionError as ae:
        app_logger.error(f"hash_output: {hash_output}, expected_hash_output: {expected_hash_output} ...")
        app_logger.error(f"error: {ae} ...")
        raise ae


class TestLambdaTTS(unittest.TestCase):
    def setUp(self):
        if platform.system() == "Windows" or platform.system() == "Win32":
            os.environ["PYTHONUTF8"] = "1"
            os.environ["IS_TESTING"] = "TRUE"

    def tearDown(self):
        if platform.system() == "Windows" or platform.system() == "Win32" and "PYTHONUTF8" in os.environ:
            del os.environ["PYTHONUTF8"]
            del os.environ["IS_TESTING"]

    def test_lambda_handler_success(self):
        set_seed()
        helper_lambda_handler(
            "Hello, this is a test!",
            [b'pbA1DQwHcJQvPE0hBFUn5tDuGjL5AhrjdCcQWWiosQo=', b"Y9H0mvDxuTxMyt1F4N2/JnVjf2SiX8w1FYVsaT7bkQU="]
        )

    def test_lambda_handler_empty_text(self):
        set_seed()
        helper_lambda_handler(
            'Hello, this is a test with special characters!\t [{]}!\\ \ °@#&*()',
            [b'5BotdLF0yqqR6+RhhmUpqeZKn4OOuK1gctt0/sw6wPw=', b"xnpJ0cUFjW4Vv9b3lWagjtUzzF3HoEBBtIle80WqOT4="]
        )


if __name__ == '__main__':
    unittest.main()
