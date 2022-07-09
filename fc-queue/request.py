from config import *
import requests

def send(payload):
    timestamp = payload["timestamp"]
    try:
        response = requests.request("GET", BACKEND_URL, headers={}, json=payload, verify=False, timeout=10).json()
        response["timestamp"] = timestamp
        return response, True
    except:
        return payload, False