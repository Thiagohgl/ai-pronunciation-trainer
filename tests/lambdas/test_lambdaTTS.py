import os
import unittest

from aip_trainer import app_logger


def exec_test_lambda_tts(text, language, expected_hash):
    import random
    from aip_trainer.lambdas import lambdaTTS
    from aip_trainer.utils import utilities

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
    assert expected_hash == output_hash
    os.unlink(output)


def assert_raises_get_tts(
    self, real_text, language, exc, error_message
):
    from aip_trainer.lambdas import lambdaTTS

    with self.assertRaises(exc):
        try:
            lambdaTTS.get_tts(real_text, language)
        except exc as e:
            self.assertEqual(str(e), error_message)
            raise e


class TestLambdaTTS(unittest.TestCase):
    def test_lambdaTTS_en_ok(self):
        try:
            exec_test_lambda_tts(
            "Hi there, how are you?",
            "en",
            b'6rZkDkF/Jc/7S5aTBlyNvntMng1+N81Flndx3WM5U0g='
            )
        except AssertionError:
            exec_test_lambda_tts(
            "Hi there, how are you?",
            "en",
            b'S7ADQbzBhmtBhYy1lLTQysv9ScAy2A0WUhG3RtWwvws='
            )

    def test_lambdaTTS_de_ok(self):
        try:
            exec_test_lambda_tts(
                "Ich bin Alex!",
                "de",
                b'4CCWiz7DOOHSmyYcS8KTBvk2E3zHtaX5umtksVln5VA='
            )
        except AssertionError:
            exec_test_lambda_tts(
                "Ich bin Alex!",
                "de",
                b'vNsDzs4ULJI2Ml0qyIrVaegI+7jK79btoq+O5FjuMEo='
            )

    def test_lambdaTTS_empty_text(self):
        assert_raises_get_tts(self, "", "fake language", ValueError, "cannot read an empty/None text: ''...")

    def test_lambdaTTS_empty_language(self):
        assert_raises_get_tts(self, "fake text", "", NotImplementedError, "Not tested/supported with '' language...")


if __name__ == "__main__":
    unittest.main()
