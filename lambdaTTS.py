import base64
import json
import os

import soundfile as sf

import AIModels
import models
import utilsFileIO
from constants import sample_rate_resample


model_TTS_lambda = AIModels.NeuralTTS(models.getTTSModel('de'), sample_rate_resample)


def lambda_handler(event, context):

    body = json.loads(event['body'])

    text_string = body['value']

    if len(text_string) == 0:
        return utilsFileIO.return_response_ok('{}')

    linear_factor = 0.2
    audio = model_TTS_lambda.getAudioFromSentence(
        text_string).detach().numpy()*linear_factor
    random_file_name = utilsFileIO.generateRandomString(20)+'.wav'

    sf.write('./'+random_file_name, audio, sample_rate_resample)

    with open(random_file_name, "rb") as f:
        audio_byte_array = f.read()

    os.remove(random_file_name)

    body = json.dumps({
        "wavBase64": str(base64.b64encode(audio_byte_array))[2:-1],
    })
    return utilsFileIO.return_response_ok(body)
