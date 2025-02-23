import os
import unittest

import lambdaTTS
from constants import app_logger
from tests import utilities


def exec_test_lambda_tts(cls, text, language, expected_hash_list):
    import random

    cls.maxDiff = None
    tmp_rnd = str(random.random())
    tmp_prefix = f"test_lambdaTTS_{language}_ok_{tmp_rnd}_"
    tmp_suffix = ".wav"
    output = lambdaTTS.get_tts(
        text, language, tmp_prefix=tmp_prefix, tmp_suffix=tmp_suffix
    )
    assert tmp_prefix in output
    assert tmp_suffix in output
    assert os.path.exists(output) and os.path.isfile(output)
    output_hash = utilities.hash_calculate(output, is_file=True, read_mode="rb")
    app_logger.info(f"output_hash '{text}', '{language}' => {output_hash}")
    cls.assertIn(output_hash, expected_hash_list)
    os.unlink(output)


def assert_raises_get_tts(cls, real_text, language, exc, error_message):
    with cls.assertRaises(exc):
        try:
            lambdaTTS.get_tts(real_text, language)
        except exc as e:
            cls.assertEqual(str(e), error_message)
            raise e


class TestLambdaTTS(unittest.TestCase):
    def test_lambdaTTS_en_ok(self):
        exec_test_lambda_tts(
            self,
            "Hi there, how are you?",
            "en",
            [
                b'6rZkDkF/Jc/7S5aTBlyNvntMng1+N81Flndx3WM5U0g=',
                b'lb3j7epbN0DuP1xKWBRIewB8A7lYZQDi6HoZdxk12Ic=',
                b'S7ADQbzBhmtBhYy1lLTQysv9ScAy2A0WUhG3RtWwvws='
            ]
        )

    def test_lambdaTTS_de_ok(self):
        exec_test_lambda_tts(
            self,
            "Ich bin Alex!",
            "de",
            [
                b'vNsDzs4ULJI2Ml0qyIrVaegI+7jK79btoq+O5FjuMEo=',
                b'4CCWiz7DOOHSmyYcS8KTBvk2E3zHtaX5umtksVln5VA=',
                b'h1qqA9SK04nt7HYbb8Co+jxeV2vo0G7bnRhGktRIXaE='
            ]
        )


    def test_lambdaTTS_empty_text(self):
        assert_raises_get_tts(self, "", "fake language", ValueError, "cannot read an empty/None text: ''...")

    def test_lambdaTTS_empty_language(self):
        assert_raises_get_tts(self, "fake text", "", NotImplementedError, "Not tested/supported with '' language...")


if __name__ == "__main__":
    unittest.main()
