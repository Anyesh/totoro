import json


def error_response(message):
    return json.loads('{"error": "' + message + '"}')
