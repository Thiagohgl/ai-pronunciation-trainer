import os
import platform
import unittest
import json
## permit to import from parent directory also in
import sys
from pathlib import Path

parent = Path(__file__).parent.parent
sys.path.append(str(parent))
from tests import EVENTS_FOLDER, set_seed
from webApp import app
from constants import ALLOWED_ORIGIN


class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        if platform.system() == "Windows" or platform.system() == "Win32":
            os.environ["PYTHONUTF8"] = "1"

    def tearDown(self):
        if (
            platform.system() == "Windows" or platform.system() == "Win32"
        ) and "PYTHONUTF8" in os.environ:
            del os.environ["PYTHONUTF8"]

    def test_main_route(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<html', response.data)

    def test_getAudioFromText(self):
        data = {'value': 'Hello, how are you?'}
        response = self.app.post('/getAudioFromText', json=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        output_data = response.data.decode("utf-8")
        output_data = json.loads(output_data)
        body_content = json.loads(output_data['body'])
        self.assertIn('wavBase64', body_content)
        self.assertNotEqual(body_content['wavBase64'], '')

    def test_getAudioFromText_empty(self):
        data = {'value': ''}
        response = self.app.post('/getAudioFromText', json=data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        output_data = response.data.decode("utf-8")
        output_data = json.loads(output_data)
        app.logger.info(f"output_data: {output_data} ...")
        # {'body': '{}', 'headers': {'Access-Control-Allow-Credentials': 'true', 'Access-Control-Allow-Headers': '*', 'Access-Control-Allow-Methods': 'OPTIONS,POST,GET', 'Access-Control-Allow-Origin': 'http://localhost:3000'}, 'statusCode': 200}
        self.assertEqual(output_data, {
            'body': '{}',
            'headers': {
                'Access-Control-Allow-Headers': ALLOWED_ORIGIN,
                'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'statusCode': 200
        })

    def test_getNext(self):
        set_seed()
        input_data = {"category": "1", "language": "de"}
        response = self.app.post('/getSample', json=input_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        output_data = response.data.decode("utf-8")
        output_data = json.loads(output_data)
        self.assertEqual(
        output_data, {
            'ipa_transcript': 'ziː vɪl niːmandɛːn haɪ̯raːtɛːn.',
            'real_transcript': ['Sie will niemanden heiraten.'],
            'transcript_translation': ''
        })

    def test_GetAccuracyFromRecordedAudio(self):
        set_seed()
        with open(EVENTS_FOLDER / "GetAccuracyFromRecordedAudio.json", "r") as src:
            inputs_outputs = json.load(src)
            inputs = inputs_outputs["inputs"]
            inputs_by_language = inputs["en"]
            loaded_body = inputs_by_language["body"]
        input_data = json.loads(loaded_body)
        pass
        response = self.app.post('/GetAccuracyFromRecordedAudio', json=input_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        output_data = response.data.decode("utf-8")
        output_data = json.loads(output_data)
        for k in [
                "real_transcript", "ipa_transcript", "pronunciation_accuracy", "real_transcripts", "matched_transcripts",
                "pair_accuracy_category", "start_time", "end_time", "is_letter_correct_all_words"
            ]:
            self.assertIn(k, output_data)

    def test_GetAccuracyFromRecordedAudio_raises_exception(self):
        set_seed()
        with open(EVENTS_FOLDER / "GetAccuracyFromRecordedAudio.json", "r") as src:
            inputs_outputs = json.load(src)
            inputs = inputs_outputs["inputs"]
            inputs_by_language = inputs["en"]
            loaded_body = inputs_by_language["body"]
        input_data = json.loads(loaded_body)
        input_data["language"] = "wrong_language"
        response = self.app.post('/GetAccuracyFromRecordedAudio', json=input_data, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        output_data = response.data.decode("utf-8")
        output_data = json.loads(output_data)
        self.assertEqual(output_data, {
            'body': '',
            'headers': {
                'Access-Control-Allow-Headers': ALLOWED_ORIGIN,
                'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'statusCode': 200
        })

if __name__ == '__main__':
    unittest.main()
