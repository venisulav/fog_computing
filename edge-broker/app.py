from flask import Flask, request, jsonify
from flask_apscheduler import APScheduler
from MsgQueue import Queue
import urllib.request

sensor_data = Queue("sensor-data",10)
processed_data = Queue("processed-data",10)
cloud_broker_ip="192.168.0.1"

def update_ip():
    external_ip = urllib.request.urlopen('https://v4.ident.me').read().decode('utf8')
    print(f"ip={external_ip}")
    #TODO: api call to cloud broker.

app = Flask(__name__)
scheduler = APScheduler()
scheduler.add_job(id = 'Scheduled Task', func=update_ip, trigger="interval", seconds=10)
scheduler.start()

@app.route('/sensorData', methods = ['POST'])
def sensorData():
    json = request.json
    sensor_data.insert(json["id"], json)
    return "success", 200

@app.route('/processedData', methods = ['POST'])
def processedData():
    json = request.json
    sensor_data.delete(json["id"])
    processed_data.insert(json["id"], json)
    return 200

@app.route('/data', methods= ['GET'])
def data():
    if not processed_data.empty():
        retVal = processed_data.pop()
    else:
        retVal =  sensor_data.pop()
    return jsonify(retVal)

if __name__ == '__main__':
    app.run(debug=True)

