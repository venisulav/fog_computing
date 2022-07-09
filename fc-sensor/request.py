from config import *
import requests

def send(payload):
    try:
        response = requests.request("GET", f"{BROKER_URL}/sensorData", headers={}, json=payload, verify=False, timeout=10).json()
        return response, True
    except:
        return payload, False