import json
from typing import Any

import pronunciationTrainer


trainer_SST_lambda = {'de': pronunciationTrainer.getTrainer("de"), 'en': pronunciationTrainer.getTrainer("en")}


def lambda_handler(event: dict[str], context: Any) -> str:
    """Lambda handler to change the model used by the pronunciation trainer (Currently not used)"""
    data = json.loads(event['body'])
    model_name = data['modelName']
    trainer_SST_lambda["de"] = pronunciationTrainer.getTrainer("de", model_name=model_name)
    trainer_SST_lambda["en"] = pronunciationTrainer.getTrainer("en", model_name=model_name)
    return f'Model changed to {model_name}!'
