import csv
import json
import shutil
import unittest
from unittest.mock import patch

import pandas as pd

import lambdaGetSample
from constants import PROJECT_ROOT_FOLDER, app_logger
from tests import EVENTS_FOLDER, set_seed, TEST_ROOT_FOLDER


def helper_category(cls, category: int, language: str, expected_output: dict):
    set_seed()
    event = {"body": json.dumps({"category": category, "language": language})}
    response = lambdaGetSample.lambda_handler(event, {})
    response_dict = json.loads(response)
    try:
        cls.assertDictEqual(response_dict, expected_output)
    except AssertionError as ae:
        app_logger.error(f"category: {category}, language: {language}.")
        app_logger.error(f"response_dict: {response_dict} .")
        app_logger.error(f"expected_output: {expected_output} .")
        raise ae


def helper_get_enriched_dataframe_csv(lang: str):
    import os

    input_df = f"test_data_{lang}.csv"
    backup_df = f"test_data2_{lang}.csv"
    shutil.copy2(EVENTS_FOLDER / input_df, EVENTS_FOLDER / backup_df)
    lambdaGetSample.get_enriched_dataframe_csv(lang, "test_data", EVENTS_FOLDER)
    with open(EVENTS_FOLDER / input_df, 'r') as src1:
        with open(PROJECT_ROOT_FOLDER / "databases" / f'data_{lang}.csv', 'r') as src2:
            csv1 = src1.readlines()
            csv2 = src2.readlines()
            assert csv1 == csv2
    shutil.copy2(EVENTS_FOLDER / backup_df, EVENTS_FOLDER / input_df)
    os.remove(EVENTS_FOLDER / backup_df)


class TestDataset(unittest.TestCase):
    def test_get_sample_by_category(self):
        count = 0
        with open(EVENTS_FOLDER / "test_lambdaGetSample.json") as src:
            json_data = json.load(src)

        for lang in ["de", "en"]:
            for cat in range(4):
                expected_output = json_data[lang][str(cat)]
                helper_category(self, cat, lang, expected_output=expected_output)
                count += 1

    def test_get_sample_using_text(self):
        body = {"language": "en", "transcript": "Hi there, how are you?"}
        event = {"body": json.dumps(body)}
        response = lambdaGetSample.lambda_handler(event, {})
        expected_output = {
            'ipa_transcript': 'haɪ ðɛr, haʊ ər ju?',
            'real_transcript': ['Hi there, how are you?'],
            'transcript_translation': ''
        }
        self.assertEqual(json.loads(response), expected_output)

    @patch.object(lambdaGetSample, "get_random_selection")
    def test_get_sample_using_text_exception(self, get_random_selection_mocked):
        with self.assertRaises(Exception):
            msg_ex = "a test exception"
            get_random_selection_mocked.side_effect = Exception(msg_ex)
            try:
                body = {"category": 1, "language": "en"}
                event = {"body": json.dumps(body)}
                lambdaGetSample.lambda_handler(event, {})
            except Exception as ex:
                assert str(ex) == msg_ex
                raise ex

    def test_get_enriched_dataframe_csv_de(self):
        helper_get_enriched_dataframe_csv("de")

    def test_get_enriched_dataframe_csv_en(self):
        helper_get_enriched_dataframe_csv("en")

    def test_getSentenceCategory(self):
        from tests import set_seed
        from lambdaGetSample import get_random_selection, getSentenceCategory

        for cat in range(1, 4):
            set_seed()
            sentence = get_random_selection("de", cat)
            cat_from_sentence = getSentenceCategory(sentence)
            assert cat == cat_from_sentence

    def test_getSentence_ValueError(self):
        from lambdaGetSample import getSentenceCategory

        with self.assertRaises(ValueError):
            try:
                getSentenceCategory("")
            except ValueError as ve:
                assert str(ve) == "category not assigned for sentence '' ..."
                raise ve


if __name__ == "__main__":
    unittest.main()
