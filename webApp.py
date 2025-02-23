import json

from flask import Flask, render_template, request
from flask_cors import CORS

import lambdaChangeModel
import lambdaGetSample
import lambdaSpeechToScore
import lambdaTTS
import utilsFileIO
from constants import IS_TESTING, STSCOREAPIKEY, app_logger


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
        app_logger.error(f"error: {e} ...")
        return utilsFileIO.return_response_ok('{}')

    return lambda_correct_output


@app.route(rootPath+'/changeModel', methods=['POST'])
def change_model():
    try:
        event = {'body': json.dumps(request.get_json(force=True))}
        lambda_correct_output = lambdaChangeModel.lambda_handler(event, {})
    except Exception as e:
        app_logger.error(f"error: {e} ...")
        return utilsFileIO.return_response('Internal server error', mimetype="application/json", status=500)
    return utilsFileIO.return_response_ok(lambda_correct_output, mimetype='text/plain')


if __name__ == "__main__":
    app_logger.info(f"IS_TESTING: {IS_TESTING}.")
    try:
        app.run(debug=IS_TESTING, host="0.0.0.0", port=3000)
    except Exception as ex:
        app_logger.error(f"main_error: type({ex}, ex.args:{ex.args}, ex:'{ex}'")
        raise ex
