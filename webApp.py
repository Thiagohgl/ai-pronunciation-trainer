from flask import Flask, render_template, request
import webbrowser
import os
from flask_cors import CORS
import json

from constants import ALLOWED_ORIGIN, app_logger
import lambdaTTS
import lambdaSpeechToScore
import lambdaGetSample


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = '*'
k = os.getenv("STScoreAPIKey", "stscore_apikey_placeholder")
data = {"STScoreAPIKey": k}

rootPath = ''


@app.route(rootPath+'/')
def main():
    return render_template('main.html', data=data)


@app.route(rootPath+'/getAudioFromText', methods=['POST'])
def getAudioFromText():
    event = {'body': json.dumps(request.get_json(force=True))}
    return lambdaTTS.lambda_handler(event, {})


@app.route(rootPath+'/getSample', methods=['POST'])
def getNext():
    event = {'body':  json.dumps(request.get_json(force=True))}
    return lambdaGetSample.lambda_handler(event, {})


@app.route(rootPath+'/GetAccuracyFromRecordedAudio', methods=['POST'])
def GetAccuracyFromRecordedAudio():

    try:
        event = {'body': json.dumps(request.get_json(force=True))}
        lambda_correct_output = lambdaSpeechToScore.lambda_handler(event, {})
    except Exception as e:
        app_logger.error(f"error: {e} ...")
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': '*',
                'Access-Control-Allow-Credentials': "true",
                'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': ''
        }

    return lambda_correct_output


if __name__ == "__main__":
    # pycharm on windows: to run in debug mode add the env variables PYTHONUTF8=1 to the file configuration
    language = 'de'
    print(os.system('pwd'))
    webbrowser.open_new('http://127.0.0.1:3000/')
    app.run(host="0.0.0.0", port=3000)
