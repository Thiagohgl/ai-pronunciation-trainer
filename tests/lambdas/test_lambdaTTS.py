import base64
import json
import tempfile
import unittest
from pathlib import Path

from lambdaSpeechToScore import audioread_load
from lambdaTTS import lambda_handler
from tests import set_seed, utilities


def helper_lambda_handler(text: str, expected_hash_output: bytes):
    set_seed()
    event = {
        'body': json.dumps({'value': text})
    }
    response = lambda_handler(event, {})
    assert response['statusCode'] == 200
    body = json.loads(response['body'])
    assert 'wavBase64' in body
    b64decoded = base64.b64decode(body['wavBase64'].encode('utf-8'))
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=True) as tmp:
        tmp.write(b64decoded)
        tmp.flush()
        tmp_name = Path(tmp.name)
        audio_array, _ = audioread_load(str(tmp_name))
    tmp_name.unlink(missing_ok=True)
    hash_output = utilities.hash_calculate(audio_array, is_file=False)
    assert hash_output == expected_hash_output


class TestLambdaTTS(unittest.TestCase):
    def test_lambda_handler_success(self):
        helper_lambda_handler(
            "Hello, this is a test!",
            b'pbA1DQwHcJQvPE0hBFUn5tDuGjL5AhrjdCcQWWiosQo='
        )

    def test_lambda_handler_empty_text(self):
        helper_lambda_handler(
            'Hello, this is a test with special characters!\t [{]}!\\ \ °@#&*()',
            b'5BotdLF0yqqR6+RhhmUpqeZKn4OOuK1gctt0/sw6wPw='
        )


if __name__ == '__main__':
    unittest.main()
