from time import sleep
from flask import Flask, request, jsonify
from flask_apscheduler import APScheduler
from MsgQueue import Queue
import requests

sensor_data = Queue("sensor-data", 20)
processed_data = Queue("processed-data", 20)
cloud_broker_ip="localhost:5003"

def update_ip():
    try:
        response = requests.get('https://v4.ident.me')
        if response.status_code == 200 :
            external_ip = response.text
            print(f"ip={external_ip}")
            response = requests.post("http://"+cloud_broker_ip+"/ip", json={"ip":external_ip})
            print("response_code",response.status_code)
    except Exception as e:
        print(e)

def send_to_cloud_broker():
    try:
        if not sensor_data.empty():
            data = sensor_data.get_not_sent()
            if data != None:
                response = requests.post("http://"+cloud_broker_ip+"/queue", json=data)
            if response.status_code == 200:
                sensor_data.mark_as_sent(data["timestamp"])
    except Exception as ex:
        print(ex)

def read_from_cloud_broker():
    try:
       response = requests.get("http://"+cloud_broker_ip+"/queue")
       if response == 200:
            json = response.json
            sensor_data.delete(json["timestamp"])
            processed_data.insert(json["timestamp"], json)
    except Exception as ex:
        print(ex)
            

app = Flask(__name__)
scheduler = APScheduler()
scheduler.add_job(id = 'Send IP', func=update_ip, trigger="interval", seconds=10)
scheduler.add_job(id = 'Send Sensor Data', func=send_to_cloud_broker, trigger="interval", seconds=2)
scheduler.add_job(id = 'Read Processed Data', func=send_to_cloud_broker, trigger="interval", seconds=2)
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

@app.route('/status', methods=['GET'])
def status():
    return ""

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5002)

