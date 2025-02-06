from flask import Flask, render_template, request
import webbrowser
import os
from flask_cors import CORS
import json

from constants import ALLOWED_ORIGIN, IS_TESTING, STSCOREAPIKEY
import lambdaTTS
import lambdaSpeechToScore
import lambdaGetSample


app = Flask(__name__)
cors = CORS(app)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Strict',
)
# if really using this api key for external requests it should be stored in a secure way
data = {"STScoreAPIKey": STSCOREAPIKEY}

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
    if IS_TESTING:
        from tests import set_seed
        print("is_testing...")
        set_seed()
    event = {'body':  json.dumps(request.get_json(force=True))}
    return lambdaGetSample.lambda_handler(event, {})


@app.route(rootPath+'/GetAccuracyFromRecordedAudio', methods=['POST'])
def GetAccuracyFromRecordedAudio():
    if IS_TESTING:
        from tests import set_seed
        print("is_testing...")
        set_seed()

    try:
        event = {'body': json.dumps(request.get_json(force=True))}
        lambda_correct_output = lambdaSpeechToScore.lambda_handler(event, {})
    except Exception as e:
        print('Error: ', str(e))
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Headers': ALLOWED_ORIGIN,
                'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': ''
        }

    return lambda_correct_output


if __name__ == "__main__":
    language = 'de'
    print(os.system('pwd'))
    webbrowser.open_new('http://127.0.0.1:3000/')
    app.run(host="0.0.0.0", port=3000)
