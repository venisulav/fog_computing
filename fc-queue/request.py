from config import *
import requests

def send(payload):
    try:
        response = requests.request("GET", BACKEND_URL, headers={}, json=payload, verify=False, timeout=10).json()
        return response, True
    except:
        return payload, False