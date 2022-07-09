from config import *
import requests

def send(payload):
    try:
        response = requests.request("POST", f"{BROKER_URL}/sensorData", headers={}, json=payload, verify=False, timeout=10)
    except Exception as ex:
        print(ex)
        return payload, False
    return response, True