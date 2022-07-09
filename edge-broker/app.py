from time import sleep
from flask import Flask, request, jsonify
from flask_apscheduler import APScheduler
from MsgQueue import Queue
import requests
import os

CLOUD_BROKER=os.environ["CLOUD_BROKER"]
HOST=os.environ["HOST"]
PORT=os.environ["PORT"]

sensor_data = Queue("sensor-data", 20)
processed_data = Queue("processed-data", 20)

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
        print(sensor_data.empty())
        if not sensor_data.empty():
            print("data here :)")
            data = sensor_data.get_not_sent()
            print(data)
            if data != None:
                print("http://"+CLOUD_BROKER+"/queue")
                response = requests.post("http://"+CLOUD_BROKER+"/queue", json=data)
            if response.status_code == 200:
                sensor_data.mark_as_sent(data["timestamp"])
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
#scheduler.add_job(id = 'Send IP', func=update_ip, trigger="interval", seconds=10)
scheduler.add_job(id = 'Send Sensor Data', func=send_to_cloud_broker, trigger="interval", seconds=2)
scheduler.add_job(id = 'Read Processed Data', func=read_from_cloud_broker, trigger="interval", seconds=2)
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

@app.route('/sensorTargets', methods= ['GET'])
def data():
    sleep(2)
    processed_data.dump()
    retVal = None
    processed = processed_data.pop()
    if processed != None:
        retVal = processed
    else:
        data =  sensor_data.pop()
        if data != None:
            retVal = {}
            if data["temprature_target"] > data["temprature"]:
                retVal["heater"] = True
            if data["temprature_target"] < data["temprature"]:
                retVal["ac"] = True
            retVal["window"] = False
    if retVal == None:
        return "Empty", 404
    return jsonify(retVal)

if __name__ == '__main__':
    app.run(debug=True, host=HOST, port=PORT)

