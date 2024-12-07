import json
import os
from pathlib import Path
import platform
import unittest

from aip_trainer import app_logger
from aip_trainer.lambdas import lambdaSpeechToScore
from tests import EVENTS_FOLDER
from tests.lambdas.constants_lambdaSpeechToScore import text_dict, expected_get_speech_to_score, expected_with_audio_files_splitted_list, expected_with_selected_word_valid_index, expected_GetAccuracyFromRecordedAudio


def set_seed(seed=0):
    import random
    import torch
    import numpy as np

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def assert_raises_get_speech_to_score_dict(cls, real_text, file_bytes_or_audiotmpfile, language, exc, error_message):
    from aip_trainer.lambdas import lambdaSpeechToScore

    with cls.assertRaises(exc):
        try:
            lambdaSpeechToScore.get_speech_to_score_dict(
                real_text,
                file_bytes_or_audiotmpfile,
                language,
                remove_random_file=False,
            )
        except exc as e:
            cls.assertEqual(str(e), error_message)
            raise e


def check_value_by_field(value, match):
    import re

    assert len(value.strip()) > 0
    for word in value.lstrip().rstrip().split(" "):
        word_check = re.findall(match, word.strip())
        assert len(word_check) == 1
        assert word_check[0] == word.strip()
    print("ok")


def check_output_by_field(output, key, match, expected_output):
    check_value_by_field(output[key], match)
    output[key] = expected_output[key]
    return output


def check_output(cls, output, expected_output, check_audio_files=False):
    from pathlib import Path

    cls.maxDiff = None
    try:
        cls.assertDictEqual(output, expected_output)
        if check_audio_files:
            audio_files = output["audio_files"]
            audio_durations = output["audio_durations"]
            for audio_duration in audio_durations:
                assert isinstance(audio_duration, float)
                assert audio_duration > 0
            for audio_file in audio_files:
                path_audio_file = Path(audio_file)
                app_logger.info(f"path_audio_file:{path_audio_file}.")
                assert path_audio_file.is_file()
                path_audio_file.unlink()
    except Exception as e:
        app_logger.error(f"e:{e}.")
        raise e


def assert_get_speech_to_score_ok(cls, language, expected):
    from aip_trainer.lambdas import lambdaSpeechToScore

    set_seed()
    path = EVENTS_FOLDER / f"test_{language}.wav"
    output = lambdaSpeechToScore.get_speech_to_score_dict(
        real_text=text_dict[language],
        file_bytes_or_audiotmpfile=str(path),
        language=language,
        remove_random_file=False,
    )
    cls.assertDictEqual(output, expected)


def assert_get_speech_to_score_ok_remove_input_file(cls, language, expected):
    import shutil
    from aip_trainer.lambdas import lambdaSpeechToScore

    set_seed()
    path = EVENTS_FOLDER / f"test_{language}.wav"
    path2 = EVENTS_FOLDER / f"test2_{language}.wav"
    shutil.copy(path, path2)
    assert path2.exists() and path2.is_file()
    output = lambdaSpeechToScore.get_speech_to_score_dict(
        real_text=text_dict[language],
        file_bytes_or_audiotmpfile=str(path2),
        language=language,
        remove_random_file=True,
    )
    assert not path2.exists()
    cls.assertDictEqual(output, expected)


def assert_get_speech_to_score_tuple_ok(cls, language, expected, expected_num_words):
    from aip_trainer.lambdas import lambdaSpeechToScore

    set_seed()
    path = EVENTS_FOLDER / f"test_{language}.wav"
    (
        real_transcripts,
        is_letter_correct_all_words,
        pronunciation_accuracy,
        ipa_transcript,
        real_transcripts_ipa,
        num_words,
        first_audio_file,
        dumped,
    ) = lambdaSpeechToScore.get_speech_to_score_tuple(
        real_text=text_dict[language],
        file_bytes_or_audiotmpfile=str(path),
        language=language,
        remove_random_file=False,
    )
    assert real_transcripts == text_dict[language]
    expected_output = expected[language]
    assert is_letter_correct_all_words.strip() == expected_output["is_letter_correct_all_words"].strip()
    assert pronunciation_accuracy == expected_output["pronunciation_accuracy"]
    assert ipa_transcript.strip() == expected_output["ipa_transcript"].strip()
    assert real_transcripts_ipa.strip() == expected_output["real_transcripts_ipa"]
    assert num_words == expected_num_words
    first_audio_file_path = Path(first_audio_file)
    assert first_audio_file_path.exists() and first_audio_file_path.is_file()
    json_loaded = json.loads(dumped)
    check_output(cls, json_loaded, expected_output, check_audio_files=True)


def assert_get_selected_word_valid_index_ok(language, expected):
    set_seed()
    path = EVENTS_FOLDER / f"test_{language}_easy.wav"
    input_text = text_dict[language]
    _, _, _, _, _, _, _, output_json = lambdaSpeechToScore.get_speech_to_score_tuple(
        input_text, str(path), language, False
    )
    idx_recorded_word = 2
    output_loaded = json.loads(output_json)
    audio_file, word, duration = lambdaSpeechToScore.get_selected_word(
        idx_recorded_word, output_json
    )
    audio_file_path = Path(audio_file)
    assert audio_file_path.exists() and audio_file_path.is_file()
    expected_end_time_list = expected[language]["audio_durations"]
    expected_end_time = expected_end_time_list[idx_recorded_word]
    assert duration == expected_end_time
    words_list = text_dict[language].split()
    assert word == words_list[idx_recorded_word]
    for file_to_del in output_loaded["audio_files"]:
        Path(file_to_del).unlink()


def assert_get_selected_word_invalid_index(cls, language):
    set_seed()
    path = EVENTS_FOLDER / f"test_{language}_easy.wav"
    _, _, _, _, _, _, _, output_json = lambdaSpeechToScore.get_speech_to_score_tuple(
        text_dict[language], str(path), language, False
    )
    with cls.assertRaises(IndexError):
        try:
            lambdaSpeechToScore.get_selected_word(120, output_json)
        except IndexError as ie:
            msg = str(ie)
            assert msg == "list index out of range"
            raise ie


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
        set_seed()
        with open(EVENTS_FOLDER / "GetAccuracyFromRecordedAudio.json", "r") as src:
            inputs_outputs = json.load(src)
        inputs = inputs_outputs["inputs"]
        for language, event_content in inputs.items():
            current_expected_output = expected_GetAccuracyFromRecordedAudio[language]
            output = lambdaSpeechToScore.lambda_handler(event_content, [])
            output = json.loads(output)
            expected_GetAccuracyFromRecordedAudio[language] = output
            app_logger.info(
                f"output type:{type(output)}, expected_output type:{type(current_expected_output)}."
            )
            self.assertDictEqual(output, current_expected_output)

    def test_lambda_handler_empty_text(self):
        from aip_trainer.lambdas import lambdaSpeechToScore

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
                "headers": {
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Credentials": "true",
                    "Access-Control-Allow-Origin": "http://127.0.0.1:3000/",
                    "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
                },
                "body": "",
            },
        )

    def test_get_speech_to_score_en_ok(self):
        assert_get_speech_to_score_ok(self, "en", expected_get_speech_to_score["en"])

    def test_get_speech_to_score_de_ok(self):
        assert_get_speech_to_score_ok(self, "de", expected_get_speech_to_score["de"])

    def test_get_speech_to_score_en_ok_remove_input_file(self):
        assert_get_speech_to_score_ok_remove_input_file(
            self, "en", expected_get_speech_to_score["en"]
        )

    def test_get_speech_to_score_de_ok_remove_input_file(self):
        assert_get_speech_to_score_ok_remove_input_file(
            self, "de", expected_get_speech_to_score["de"]
        )

    def test_get_speech_to_score_tuple_de_ok(self):
        assert_get_speech_to_score_tuple_ok(
            self, "de", expected_with_audio_files_splitted_list, expected_num_words=5
        )

    def test_get_speech_to_score_tuple_en_ok(self):
        assert_get_speech_to_score_tuple_ok(
            self, "en", expected_with_audio_files_splitted_list, expected_num_words=5
        )

    def test_get_speech_to_score_dict__de_empty_input_text(self):
        language = "de"
        path = EVENTS_FOLDER / f"test_{language}.wav"
        assert_raises_get_speech_to_score_dict(
            self,
            "",
            str(path),
            language,
            ValueError,
            "cannot read an empty/None text: ''...",
        )

    def test_get_speech_to_score_dict__en_empty_input_text(self):
        language = "en"
        path = EVENTS_FOLDER / f"test_{language}.wav"
        assert_raises_get_speech_to_score_dict(
            self,
            "",
            str(path),
            language,
            ValueError,
            "cannot read an empty/None text: ''...",
        )

    def test_get_speech_to_score_dict__de_empty_input_file(self):
        language = "de"
        assert_raises_get_speech_to_score_dict(
            self,
            "text fake",
            "",
            language,
            OSError,
            "cannot read an empty/None file: ''...",
        )

    def test_get_speech_to_score_dict__en_empty_input_file(self):
        language = "en"
        assert_raises_get_speech_to_score_dict(
            self,
            "text fake",
            "",
            language,
            OSError,
            "cannot read an empty/None file: ''...",
        )

    def test_get_speech_to_score_dict__empty_language(self):
        assert_raises_get_speech_to_score_dict(
            self,
            "text fake",
            "fake_file",
            "",
            NotImplementedError,
            "Not tested/supported with '' language...",
        )

    def test_get_speech_to_score_dict__empty_language(self):
        language = "en"
        path_file = str(EVENTS_FOLDER / "empty_file.wav")
        assert_raises_get_speech_to_score_dict(
            self,
            "text fake",
            path_file,
            language,
            OSError,
            f"cannot read an empty file: '{path_file}'...",
        )

    def test_get_selected_word_valid_index_de_ok(self):
        assert_get_selected_word_valid_index_ok(
            "de", expected_with_selected_word_valid_index
        )

    def test_get_selected_word_valid_index_en_ok(self):
        assert_get_selected_word_valid_index_ok(
            "en", expected_with_selected_word_valid_index
        )

    def test_get_selected_word_invalid_index_de(self):
        assert_get_selected_word_invalid_index(self, "de")

    def test_get_selected_word_invalid_index_en(self):
        assert_get_selected_word_invalid_index(self, "en")

    def test_get_selected_word_empty_transcripts(self):
        raw_json_output = json.dumps(
            {"audio_files": [], "real_transcripts": "", "audio_durations": []}
        )
        idx_recorded_word = 0
        with self.assertRaises(IndexError):
            lambdaSpeechToScore.get_selected_word(idx_recorded_word, raw_json_output)

    def test_get_splitted_audio_file_valid_input(self):
        language = "en"
        path = str(EVENTS_FOLDER / f"test_{language}.wav")
        start_time = [0.0, 1.0, 2.0]
        end_time = [1.0, 2.0, 2.5]

        audio_files, audio_durations = lambdaSpeechToScore.get_splitted_audio_file(
            audiotmpfile=path, start_time=start_time, end_time=end_time
        )

        assert len(audio_files) == len(start_time)
        assert len(audio_durations) == len(start_time)
        for audio_file, duration in zip(audio_files, audio_durations):
            audio_file_path = Path(audio_file)
            assert audio_file_path.exists() and audio_file_path.is_file()
            assert duration > 0
            audio_file_path.unlink()

    def test_get_splitted_audio_file_invalid_input(self):
        from soundfile import LibsndfileError

        start_time = [0.0, 1.0, 2.0]
        end_time = [1.0, 2.0, 2.5]

        with self.assertRaises(LibsndfileError):
            try:
                lambdaSpeechToScore.get_splitted_audio_file(
                    audiotmpfile="", start_time=start_time, end_time=end_time
                )
            except LibsndfileError as lsfe:
                msg = str(lsfe)
                assert msg == "Error opening '': System error."
                raise lsfe

    def test_get_splitted_audio_file_mismatched_times(self):
        from soundfile import LibsndfileError

        language = "en"
        path = EVENTS_FOLDER / f"test_{language}.wav"
        start_time = [4.0, 5.0, 7.0]
        end_time = [3.0, 4.0, 5.5]

        with self.assertRaises(LibsndfileError):
            try:
                lambdaSpeechToScore.get_splitted_audio_file(
                    audiotmpfile=str(path), start_time=start_time, end_time=end_time
                )
            except LibsndfileError as lsfe:
                msg = str(lsfe)
                assert msg == "Internal psf_fseek() failed."
                raise lsfe


if __name__ == "__main__":
    unittest.main()
