from threading import Lock
from time import sleep
from flask import Flask, request, jsonify
from flask_apscheduler import APScheduler
from MsgQueue import Queue
import requests
import os
from datetime import datetime

CLOUD_BROKER=os.environ["CLOUD_BROKER"]
HOST=os.environ["HOST"]
PORT=os.environ["PORT"]

sensor_data = Queue("sensor-data", 50)
processed_data = Queue("processed-data", 50)

lock = Lock()
last_sent_ts = datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")

def check_and_set_last_sent_ts(ts):
    global last_sent_ts
    with lock:
        date=datetime.strptime(ts, "%Y-%m-%d %H:%M:%S")
        if date > last_sent_ts:
            last_sent_ts = date
            return True
        return False

def update_ip():
    try:
        response = requests.get('https://v4.ident.me')
        if response.status_code == 200 :
            external_ip = response.text
            print(f"ip={external_ip}")
            response = requests.post("http://"+CLOUD_BROKER+"/ip", json={"ip":external_ip})
            print("response_code",response.status_code)
    except Exception as e:
        print(e)

def send_to_cloud_broker():
    try:
        if not sensor_data.empty():
            data = sensor_data.get_not_sent()
            if data != None:
                print("http://"+CLOUD_BROKER+"/queue")
                response = requests.post("http://"+CLOUD_BROKER+"/queue", json=data)
            if response.status_code == 200:
                sensor_data.mark_as_sent(data["timestamp"])
            elif response.status_code == 409:
                sensor_data.delete(data['timestamp'])
            else:
                print(f'HTTP Error while writing to cloud broker: {response.status_code} \n {response.text}')
    except Exception as ex:
        print(f'Error while writing to cloud broker: {ex}')

def read_from_cloud_broker():
    try:
        response = requests.get("http://"+CLOUD_BROKER+"/queue")
        if response.status_code == 200:
            json = response.json()
            sensor_data.delete(json["timestamp"])
            processed_data.insert(json["timestamp"], json)
        elif response.status_code != 404:
            print(f'HTTP Error while reading from cloud broker: {response.status_code}')

    except Exception as ex:
        print(f'Error while reading from cloud broker: {ex}')
            

app = Flask(__name__)
scheduler = APScheduler()

scheduler.add_job(id = 'Send Sensor Data', func=send_to_cloud_broker, trigger="interval", seconds=10)
scheduler.add_job(id = 'Read Processed Data', func=read_from_cloud_broker, trigger="interval", seconds=10)
scheduler.start()

@app.route('/sensorData', methods = ['POST'])
def sensorData():
    json = request.json
    sensor_data.insert(json["timestamp"], json)
    return "success", 200

@app.route('/processedData', methods = ['POST'])
def processedData():
    json = request.json
    sensor_data.delete(json["timestamp"])
    processed_data.insert(json["timestamp"], json)
    return 200

@app.route('/sensorQueue', methods= ['GET'])
def sensorQueuePop():
    while True:
        data = sensor_data.pop()
        if (data == None or check_and_set_last_sent_ts(data['timestamp']) == True):
            break
    if data != None:
        retVal=locally_process(data)
    if data == None:
        return "Empty", 404
    return jsonify(retVal)

@app.route('/processedQueue', methods= ['GET'])
def processedQueuePop():
    data = processed_data.pop()
    if data == None:
        return "Empty", 404
    return jsonify(data)

def locally_process(data):
    retVal = {}
    if data["temprature_target"] > data["temprature"]:
        retVal["heater"] = True
    else:
        retVal["heater"] = False
    if data["temprature_target"] < data["temprature"]:
        retVal["ac"] = True
    else:
        retVal["ac"] = False
    retVal["window"] = False
    return retVal

if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)

