import requests
from requests.models import HTTPError


def get_response(message="", result={}, status=False, status_code=200):
    return {
        "message": message,
        "result": result,
        "status": status,
        "status_code": status_code,
    }


def get_client_ip():

    try:
        return requests.get("http://ip.jsontest.com/").json()
    except HTTPError:
        return {"ip": ""}
