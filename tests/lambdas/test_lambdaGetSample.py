import json
import unittest

from aip_trainer.lambdas import lambdaGetSample
from tests import TEST_ROOT_FOLDER
from numpy.random import seed

expected_output__get_random_selection = [
    "Er ist ein begeisterter Theaterliebhaber.",
    ["Du hast schon den ganzen Morgen gute Laune."],
    "Tom hat mir gerade das Leben gerettet.",
    ["Kannst du mich jetzt hören?"],
    "Falls es eine bessere Lösung geben sollte, werde ich Sie umgehend informieren.",
    ["Die Kette, die du mir vor zehn Jahren geschenkt hast, liegt mir bis heute sehr am Herzen."],
    "Es lässt sich nicht in Worte fassen, wie glücklich ich gerade bin!“ – So ist es aber ganz gut in Worte gefasst.“",
    ["Als nur ein Beispiel dafür, wie Automatisierung der Menschheit zugute kommen kann, nehme man eine Roboterhand, mit deren Hilfe man unreine oder gefährliche Arbeiten verrichten kann."],
    "Since I was really tired I went to sleep early.",
    ["She accused me of being a liar."],
    "They lived in the land of Cockaigne.",
    ["This is a complicated question to answer."],
    "We are still hoping that Tom will get better.",
    ["Tom said something, but I couldn't hear what he said."],
    "People who starve themselves and mask themselves so that they can conform to what society deems beautiful are only hurting themselves.",
    ["The queen has the ability to move as much as if she were a rook, that is, over the rows and columns, as if she were a bishop, that is, over the diagonals."],
]


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


class TestLambdaGetSample(unittest.TestCase):
    def test_get_random_selection(self):
        seed(0)
        count = 0
        for lang in ["de", "en"]:
            for cat in range(4):
                for is_gradio_output in [True, False]:
                    output = lambdaGetSample.get_random_selection(
                        lang, cat, is_gradio_output=is_gradio_output
                    )
                    self.assertEqual(output, expected_output__get_random_selection[count])
                    count += 1


class TestDataset(unittest.TestCase):
    def test_random_sentences_de(self):
        expected = {'real_transcript': 'Er ist ein begeisterter Theaterliebhaber.', 'ipa_transcript': 'ɛɐ̯ ɪst aɪ̯n bɛːɡaɪ̯stɛːrtɛːr tɛːaːtɛːrliːbhaːbɛːr.', 'transcript_translation': ''}
        helper_category(self, 0, "de", expected_output=expected)

    def test_easy_sentences_easy_de(self):
        expected = {'real_transcript': 'Sie will niemanden heiraten.', 'ipa_transcript': 'ziː vɪl niːmandɛːn haɪ̯raːtɛːn.', 'transcript_translation': ''}
        helper_category(self, 1, "de", expected_output=expected)

    def test_normal_sentences_medium_de(self):
        expected = {'real_transcript': 'Leg das Buch dorthin, wo du es gefunden hast.', 'ipa_transcript': 'lɛːɡ daːs bʊx doːrtiːn, voː duː ɛːs ɡɛːfʊndɛːn hast.', 'transcript_translation': ''}
        helper_category(self, 2, "de", expected_output=expected)

    def test_hard_sentences_hard_de(self):
        expected = {'real_transcript': 'Eine Frau braucht neun Monate, um ein Kind zur Welt zu bringen, aber das heißt nicht, dass es neun zusammen in einem Monat schaffen könnten.', 'ipa_transcript': 'aɪ̯nɛː fraʊ̯ braʊ̯xt nɔɪ̯n moːnaːtɛː, uːm aɪ̯n kɪnd t͡suːr vɛlt t͡suː brɪŋɛːn, aːbɛːr daːs haɪ̯st nɪçt, das ɛːs nɔɪ̯n t͡suːzamɛːn iːn aɪ̯nɛːm moːnaːt ʃafɛːn kœntɛːn.', 'transcript_translation': ''}
        helper_category(self, 3, "de", expected_output=expected)
    
    def test_random_sentences_en(self):
        expected = {'real_transcript': 'He is a passionate theatregoer.', 'ipa_transcript': 'hi ɪz ə ˈpæʃənət theatregoer.', 'transcript_translation': ''}
        helper_category(self, 0, "en", expected_output=expected)

    def test_easy_sentences_easy_en(self):
        expected = {'real_transcript': 'Lemons are usually sour.', 'ipa_transcript': 'ˈlɛmənz ər ˈjuʒəwəli saʊər.', 'transcript_translation': ''}
        helper_category(self, 1, "en", expected_output=expected)

    def test_normal_sentences_medium_en(self):
        expected = {'real_transcript': 'Tom read the Bible in its entirety, from the beginning to the end.', 'ipa_transcript': 'tɑm rɛd ðə ˈbaɪbəl ɪn ɪts ɪnˈtaɪərti, frəm ðə bɪˈgɪnɪŋ tɪ ðə ɛnd.', 'transcript_translation': ''}
        helper_category(self, 2, "en", expected_output=expected)

    def test_hard_sentences_hard_en(self):
        expected = {'real_transcript': 'That was the first time, in the history of chess, that a machine (Deep Blue) defeated a Grand Master (Garry Kasparov).', 'ipa_transcript': 'ðət wɑz ðə fərst taɪm, ɪn ðə ˈhɪstəri əv ʧɛs, ðət ə məˈʃin (dip blu) dɪˈfitɪd ə grænd ˈmæstər (ˈgɛri ˈkæspərɑv).', 'transcript_translation': ''}
        helper_category(self, 3, "en", expected_output=expected)

    def test_get_pickle2json_dataframe(self):
        import os

        custom_filename = 'test_data_de_en_2'
        lambdaGetSample.get_pickle2json_dataframe(custom_filename, TEST_ROOT_FOLDER)
        with open(TEST_ROOT_FOLDER / f'{custom_filename}.json', 'r') as src1:
            with open(TEST_ROOT_FOLDER / f'{custom_filename}_expected.json', 'r') as src2:
                json1 = json.load(src1)
                json2 = json.load(src2)
                assert json1 == json2
        os.remove(TEST_ROOT_FOLDER / f'{custom_filename}.json')


if __name__ == "__main__":
    unittest.main()
