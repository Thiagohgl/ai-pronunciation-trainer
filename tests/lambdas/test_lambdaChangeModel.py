import json
import unittest

from constants import app_logger


def helper_change_model_wrapper(cls, model_name, instance_class):
    from lambdaChangeModel import lambda_handler, trainer_SST_lambda
    body = {"modelName": model_name}
    event = {'body': json.dumps(body)}
    app_logger.info(f"Event: {event}")
    response = lambda_handler(event, {})
    cls.assertEqual(response, f'Model changed to {model_name}!')
    for language in ["de", "en"]:
        asr_model = trainer_SST_lambda[language].asr_model
        cls.assertIsInstance(asr_model, instance_class)


class TestChangeModel(unittest.TestCase):
    def test_change_model(self):
        from AIModels import NeuralASR
        from faster_whisper_wrapper import FasterWhisperASRModel
        from whisper_wrapper import WhisperASRModel

        helper_change_model_wrapper(self, 'silero', NeuralASR)
        helper_change_model_wrapper(self, 'faster_whisper', FasterWhisperASRModel)
        helper_change_model_wrapper(self, 'whisper', WhisperASRModel)


if __name__ == '__main__':
    unittest.main()
