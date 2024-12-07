import json
import os
import webbrowser

from aip_trainer import app_logger, log_level
from flask import Flask, render_template, request
from flask_cors import CORS

from aip_trainer.lambdas import lambdaGetSample
from aip_trainer.lambdas import lambdaSpeechToScore


app = Flask(__name__, template_folder="static")
cors = CORS(app)
app.config['CORS_HEADERS'] = '*'

rootPath = ''


@app.route(rootPath+'/')
def main():
    return render_template('main.html')


@app.route(rootPath+'/getSample', methods=['POST'])
def getNext():
    event = {'body':  json.dumps(request.get_json(force=True))}
    return lambdaGetSample.lambda_handler(event, [])


@app.route(rootPath+'/GetAccuracyFromRecordedAudio', methods=['POST'])
def GetAccuracyFromRecordedAudio():
    try:
        event = {'body': json.dumps(request.get_json(force=True))}
        lambda_correct_output = lambdaSpeechToScore.lambda_handler(event, [])
        return lambda_correct_output
    except Exception as e:
        import traceback
        app_logger.error(e)
        app_logger.error(traceback.format_exc())
        raise e


if __name__ == "__main__":
    is_docker_container = os.getenv("IS_DOCKER_CONTAINER", "").lower() == "yes"
    app_logger.info(f"is_docker_container:{is_docker_container}.")
    hostname = "127.0.0.1" if is_docker_container else "0.0.0.0"
    if not is_docker_container:
        import webbrowser
        webbrowser.open_new('http://127.0.0.1:3000/')
    app.run(host=hostname, port=3000, debug=log_level=="DEBUG")
