import json
import os
import platform
import unittest
## permit to import from parent directory also in
import sys
from pathlib import Path

parent = Path(__file__).parent.parent.parent
sys.path.append(str(parent))
print(f"## sys.path:{sys.path}.")

import lambdaSpeechToScore
from constants import app_logger
from tests import EVENTS_FOLDER, set_seed
from tests.lambdas.constants_test_lambdaSpeechToScore import text_dict


def assert_raises_get_speech_to_score_dict(cls, real_text, file_bytes_or_audiotmpfile, language, exc, error_message):
    with cls.assertRaises(exc):
        try:
            lambdaSpeechToScore.get_speech_to_score_dict(
                real_text,
                file_bytes_or_audiotmpfile,
                language,
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


def check_output_with_splitted_audio_files(cls, output, expected_output, check_audio_files=False):
    from pathlib import Path

    cls.maxDiff = None
    try:
        assert_without_fields(cls, output, expected_output)
        if check_audio_files:
            audio_files = output["audio_files"]
            audio_durations = output["audio_durations"]
            for audio_duration in audio_durations:
                assert isinstance(audio_duration, float)
                assert audio_duration > 0
            for audio_file in audio_files:
                audio_file = EVENTS_FOLDER / audio_file
                path_audio_file = Path(audio_file)
                app_logger.info(f"path_audio_file:{path_audio_file}.")
                assert path_audio_file.is_file()
                path_audio_file.unlink()
    except Exception as e:
        app_logger.error(f"e:{e}.")
        raise e

def check_start_end_time(output):
    # split the string list into a list of floats then assert the values are greater than 0
    start_time_list = [float(x) for x in output["start_time"].split()]
    end_time_list = [float(x) for x in output["end_time"].split()]
    assert " ".join([str(x) for x in start_time_list]) == output["start_time"]
    assert " ".join([str(x) for x in end_time_list]) == output["end_time"]
    ## for some reason whisper even when seed is set keeps changing the start_time and end_time lists
    # todo: check why the start_time and end_time are not the same as the expected ones
    # count = 0
    # for start_time, end_time in zip(start_time_list, end_time_list):
    #     if count > 0:
    #         assert start_time >= start_time_list[count - 1], f"start_time:{start_time} (idx:{count}) should be greater than previous element:{start_time_list[count - 1]}, start_time_list:{start_time_list}."
    #         assert end_time >= end_time_list[count - 1], f"end_time:{end_time} (idx:{count}) should be greater than previous element:{end_time_list[count - 1]}, end_time_list:{end_time_list}."
    #         assert start_time > 0, f"start_time:{start_time} (idx:{count}) should be greater or EQUAL than 0, start_time_list:{start_time_list}."
    #     if count == 0:
    #         assert start_time >= 0, f"start_time:{start_time} (idx:{count}) should be greater than 0, start_time_list:{start_time_list}."
    #     assert end_time > 0, f"end_time:{end_time} (idx:{count}) should be greater than 0, end_time_list:{end_time_list}."
    #     assert start_time < end_time, f"start_time:{start_time} should be less than end_time:{end_time}."
    #     count += 1


def assert_without_fields(cls, output, expected_output, fields_to_avoid="start_time,end_time,audio_files,audio_durations"):
    try:
        check_start_end_time(output)
        fields_to_avoid = fields_to_avoid.strip()
        output = {k:v for k, v in output.items() if k not in fields_to_avoid}
        tmp_expected = {k:v for k, v in expected_output.items() if k not in fields_to_avoid}
        app_logger.info(f"check_start_end_time>output:{output}.")
        app_logger.info(f"check_start_end_time>tmp_expected:{tmp_expected}.")
        cls.assertDictEqual(output, tmp_expected)
    except Exception as ex:
        app_logger.error(f"ex:{ex}.")
        app_logger.error(f"output:{output}.")
        app_logger.error(f"expected_output (with all the fields):{expected_output}.")
        raise ex


def assert_get_speech_to_score_ok(cls, language):
    cls.maxDiff = None
    set_seed()
    path = EVENTS_FOLDER / f"test_{language}_easy.wav"
    output = lambdaSpeechToScore.get_speech_to_score_dict(
        real_text=text_dict[language],
        file_bytes_or_audiotmpfile=str(path),
        language=language,
    )
    random_file_name = output["random_file_name"]
    assert isinstance(random_file_name, str)
    Path(random_file_name).is_file()
    tmp_output = {k:v for k, v in output.items() if k != "random_file_name"}
    json_path = EVENTS_FOLDER / f"expected_get_speech_to_score_ok_{language}.json"
    # with open(json_path, "w") as dst:
    #     json.dump(tmp_output, dst)
    with open(json_path, "r") as src:
        expected = json.load(src)
    assert_without_fields(cls, tmp_output, expected)


# def assert_get_speech_to_score_ok_remove_input_file(cls, language, expected):
#     import shutil
#     cls.maxDiff = None
#
#     set_seed()
#     path = EVENTS_FOLDER / f"test_{language}_easy.wav"
#     path2 = EVENTS_FOLDER / f"test2_{language}_easy.wav"
#     shutil.copy(path, path2)
#     assert path2.exists() and path2.is_file()
#     output = lambdaSpeechToScore.get_speech_to_score_dict(
#         real_text=text_dict[language],
#         file_bytes_or_audiotmpfile=str(path2),
#         language=language,
#     )
#     assert not path2.exists()
#     assert_without_fields(cls, output, expected)


def assert_get_speech_to_score_tuple_ok(cls, language, expected_num_words, remove_random_file: bool):
    import glob
    import shutil
    set_seed()
    path = EVENTS_FOLDER / f"test_{language}_easy.wav"
    path2 = EVENTS_FOLDER / f"test2_{language}_easy.wav"
    if remove_random_file:
        shutil.copy(path, path2)
        path = path2
    (
        real_transcripts,
        is_letter_correct_all_words,
        pronunciation_accuracy,
        ipa_transcript,
        real_transcripts_ipa,
        num_words,
        first_audio_file,
        dumped,
        random_file_name
    ) = lambdaSpeechToScore.get_speech_to_score_tuple(
        real_text=text_dict[language],
        file_bytes_or_audiotmpfile=str(path),
        language=language,
        remove_random_file=remove_random_file,
    )
    json_path = EVENTS_FOLDER / f"expected_get_speech_to_score_tuple_ok_{language}.json"
    app_logger.info(f"json_path:{json_path} .")
    # with open(json_path, "w") as dst:
    #     json_loaded = {k:v for k, v in json.loads(dumped).items() if k != "random_file_name"}
    #     expected = {
    #         "real_transcripts": real_transcripts,
    #         "is_letter_correct_all_words": is_letter_correct_all_words,
    #         "pronunciation_accuracy": pronunciation_accuracy,
    #         "ipa_transcript": ipa_transcript,
    #         "real_transcripts_ipa": real_transcripts_ipa,
    #         "num_words": num_words,
    #         "dumped": json_loaded
    #     }
    #     json.dump(expected, dst)
    assert real_transcripts == text_dict[language]
    with open(json_path, "r") as src:
        expected_output = json.load(src)
    assert is_letter_correct_all_words.strip() == expected_output["is_letter_correct_all_words"].strip()
    assert pronunciation_accuracy == expected_output["pronunciation_accuracy"]
    assert ipa_transcript.strip() == expected_output["ipa_transcript"].strip()
    assert real_transcripts_ipa.strip() == expected_output["real_transcripts_ipa"]
    assert num_words == expected_num_words
    first_audio_file_path = Path(first_audio_file)
    assert first_audio_file_path.exists() and first_audio_file_path.is_file()
    if not remove_random_file:
        assert Path(random_file_name).is_file()
    json_loaded = json.loads(dumped)
    check_output_with_splitted_audio_files(cls, json_loaded, expected_output["dumped"], check_audio_files=True)
    # workaround to remove the tmp audio files created during these assertion tests
    files_to_remove_list = str(EVENTS_FOLDER / "test2*")
    if remove_random_file:
        for file_to_del in glob.glob(files_to_remove_list):
            assert Path(file_to_del).is_file()
            Path(file_to_del).unlink()


def assert_get_selected_word_valid_index_ok(language):
    import numpy as np
    set_seed()
    path = EVENTS_FOLDER / f"test_{language}_easy.wav"
    tmp_audio_loaded, tmp_audio_samplerate = lambdaSpeechToScore.soundfile_load(path)
    tmp_audio_loaded = np.asarray(tmp_audio_loaded)
    duration_tot = tmp_audio_loaded.size / tmp_audio_samplerate
    input_text = text_dict[language]
    _, _, _, _, _, _, _, output_json, _ = lambdaSpeechToScore.get_speech_to_score_tuple(
        input_text, str(path), language, False
    )
    idx_recorded_word = 2
    output_loaded = json.loads(output_json)
    audio_file, word, duration = lambdaSpeechToScore.get_selected_word(
        idx_recorded_word, output_json
    )
    try:
        audio_file_path = Path(audio_file)
        assert audio_file_path.exists() and audio_file_path.is_file()
        assert isinstance(duration, float)
        assert 0 < duration < duration_tot
        # assert duration == expected_end_time
        words_list = text_dict[language].split()
        assert word == words_list[idx_recorded_word]
        for file_to_del in output_loaded["audio_files"]:
            Path(file_to_del).unlink()
    except Exception as ex:
        app_logger.error(f"ex:{ex}.")
        raise ex


def assert_get_selected_word_invalid_index(cls, language):
    import glob
    set_seed()
    path = EVENTS_FOLDER / f"test_{language}_easy.wav"
    _, _, _, _, _, _, _, output_json, _ = lambdaSpeechToScore.get_speech_to_score_tuple(
        text_dict[language], str(path), language, False
    )
    with cls.assertRaises(IndexError):
        try:
            lambdaSpeechToScore.get_selected_word(120, output_json)
        except IndexError as ie:
            msg = str(ie)
            assert msg == "list index out of range"
            raise ie
    for file_to_del in glob.glob(f"{EVENTS_FOLDER / path.stem}_*"):
        assert Path(file_to_del).is_file()
        Path(file_to_del).unlink()


def helper_get_accuracy_from_recorded_audio(cls, source, use_dtw: bool = None):
    with open(EVENTS_FOLDER / "GetAccuracyFromRecordedAudio.json", "r") as src:
        inputs_outputs = json.load(src)
    inputs = inputs_outputs["inputs"]
    for language, event_content in inputs.items():
        set_seed()
        event_content_loaded = json.loads(event_content["body"])
        if use_dtw is not None:
            event_content_loaded["useDTW"] = use_dtw
        else:
            del event_content_loaded["useDTW"]
        event_content["body"] = json.dumps(event_content_loaded)
        output = lambdaSpeechToScore.lambda_handler(event_content, {})
        output = {k:v for k, v in json.loads(output).items() if k != "random_file_name"}
        json_path = EVENTS_FOLDER / f"expected_get_accuracy_from_recorded_audio_{language}_{source}_dtw{use_dtw}.json"
        app_logger.info(f"json_path:{json_path} .")
        # with open(json_path, "w") as dst:
        #     json.dump(output, dst)
        with open(json_path, "r") as src:
            current_expected_output_loaded = json.load(src)
        try:
            cls.assertDictEqual(output, current_expected_output_loaded)
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

    def test_GetAccuracyFromRecordedAudio_dtw_none(self):
        self.maxDiff = None
        try:
            helper_get_accuracy_from_recorded_audio(self, "cmd", None)
        except AssertionError:
            helper_get_accuracy_from_recorded_audio(self, "gui", None)

    def test_GetAccuracyFromRecordedAudio_dtw_false(self):
        self.maxDiff = None
        try:
            helper_get_accuracy_from_recorded_audio(self, "cmd", False)
        except AssertionError:
            helper_get_accuracy_from_recorded_audio(self, "gui", False)

    def test_GetAccuracyFromRecordedAudio_dtw_true(self):
        self.maxDiff = None
        try:
            helper_get_accuracy_from_recorded_audio(self, "cmd", True)
        except AssertionError:
            helper_get_accuracy_from_recorded_audio(self, "gui", True)

    def test_lambda_handler_empty_text(self):
        from flask import Response
        with open(EVENTS_FOLDER / "GetAccuracyFromRecordedAudio.json", "r") as src:
            inputs_outputs = json.load(src)
        event = inputs_outputs["inputs"]["en"]
        event_body = event["body"]
        event_body_loaded = json.loads(event_body)
        event_body_loaded["title"] = ""
        event_body = json.dumps(event_body_loaded)
        event["body"] = event_body
        output = lambdaSpeechToScore.lambda_handler(event, {})
        self.assertIsInstance(output, Response)
        self.assertDictEqual(output.json, {})

    def test_get_speech_to_score_en_ok(self):
        assert_get_speech_to_score_ok(self, "en")

    def test_get_speech_to_score_de_ok1(self):
        assert_get_speech_to_score_ok(self, "de")

    # def test_get_speech_to_score_en_ok_remove_input_file(self):
    #     assert_get_speech_to_score_ok_remove_input_file(
    #         self, "en", expected_get_speech_to_score["en"]
    #     )
    #
    # def test_get_speech_to_score_de_ok_remove_input_file(self):
    #     assert_get_speech_to_score_ok_remove_input_file(
    #         self, "de", expected_get_speech_to_score["de"]
    #     )

    def test_get_speech_to_score_tuple_de_ok_not_remove_random_file(self):
        assert_get_speech_to_score_tuple_ok(
            self, "de", expected_num_words=5, remove_random_file=False
        )

    def test_get_speech_to_score_tuple_en_ok_not_remove_random_file(self):
        assert_get_speech_to_score_tuple_ok(
            self, "en", expected_num_words=5, remove_random_file=False
        )

    def test_get_speech_to_score_tuple_de_ok_remove_random_file(self):
        assert_get_speech_to_score_tuple_ok(
            self, "de", expected_num_words=5, remove_random_file=True
        )

    def test_get_speech_to_score_tuple_en_ok_remove_random_file(self):
        assert_get_speech_to_score_tuple_ok(
            self, "en", expected_num_words=5, remove_random_file=True
        )

    def test_get_speech_to_score_dict__de_empty_input_text(self):
        language = "de"
        path = EVENTS_FOLDER / f"test_{language}_easy.wav"
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
        path = EVENTS_FOLDER / f"test_{language}_easy.wav"
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

    def test_get_speech_to_score_dict__empty_language1(self):
        assert_raises_get_speech_to_score_dict(
            self,
            "text fake",
            "fake_file",
            "",
            NotImplementedError,
            "Not tested/supported with '' language...",
        )

    def test_get_speech_to_score_dict__empty_language2(self):
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
        assert_get_selected_word_valid_index_ok("de")

    def test_get_selected_word_valid_index_en_ok(self):
        assert_get_selected_word_valid_index_ok("en")

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
        path = str(EVENTS_FOLDER / f"test_{language}_hard.wav")
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
        path = EVENTS_FOLDER / f"test_{language}_easy.wav"
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
