import string
import random

from constants import ALLOWED_ORIGIN


headers = {
    'Access-Control-Allow-Headers': ALLOWED_ORIGIN,
    'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
    'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
}


def generateRandomString(str_length: int = 20):
    # printing lowercase
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(str_length))


def return_response(body, mimetype="application/json", status=200):
    from flask import Response
    return Response(
        response=body,
        status=status,
        mimetype=mimetype,
        headers=headers
    )


def return_response_ok(body, mimetype="application/json"):
    return return_response(body, mimetype, 200)
