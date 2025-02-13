import string
import random


def generateRandomString(str_length: int = 20):
    # printing lowercase
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(str_length))


def return_response_ok(body):
    from constants import ALLOWED_ORIGIN
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': ALLOWED_ORIGIN,
            'Access-Control-Allow-Origin': ALLOWED_ORIGIN,
            'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
        },
        'body': body
    }
