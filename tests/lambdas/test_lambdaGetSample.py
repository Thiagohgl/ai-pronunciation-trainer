import json
import unittest

import lambdaGetSample
from tests import EVENTS_FOLDER
from random import seed


def helper_category(cls, category: int, language: str, expected_output: dict):
    seed(0)
    event = {"body": json.dumps({"category": category, "language": language})}
    response = lambdaGetSample.lambda_handler(event, [])
    response_dict = json.loads(response)
    try:
        cls.assertDictEqual(response_dict, expected_output)
    except AssertionError as ae:
        print(f"category: {category}, language: {language}.")
        print(f"response_dict: {response_dict}")
        print(f"expected_output: {expected_output}")
        raise ae


class TestDataset(unittest.TestCase):
    def test_get_sample(self):
        seed(0)
        count = 0
        with open(EVENTS_FOLDER / "test_lambdaGetSample.json") as src:
            json_data = json.load(src)

        for lang in ["de", "en"]:
            for cat in range(4):
                expected_output = json_data[lang][str(cat)]
                helper_category(self, cat, lang, expected_output=expected_output)
                count += 1


if __name__ == "__main__":
    unittest.main()
