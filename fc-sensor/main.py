from apscheduler.schedulers.background import BlockingScheduler
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_humidity_v2 import BrickletHumidityV2
from tinkerforge.bricklet_uv_light import BrickletUVLight
from flask import Flask
from flask_restful import Resource, Api, reqparse
import time
import datetime
import shelve
from threading import Lock
from request import send
from config import *

app = Flask("SensorApp")
api = Api(app)

target_lock = Lock()

# HOST = "host.docker.internal"
HOST = "localhost"
PORT = 4223
UID_H = "HF1" # UID of Humidity Bricklet 2.0
UID_UV = "xkb" # UID of UV Light Bricklet

"""
TODO:
	- create timestamp in correct format - done
	- incorporate targets - done
		- tragets should be persistent and settable - done
	- send to local broker
"""
def getTargets():
	target_lock.acquire()
	db = shelve.open("targets", writeback=False)
	target_dict = {}
	for key in db:
		target_dict[key] = db[key]
	target_lock.release()
	if len(target_dict) <= 0:
		target_dict = DEFAULT_TARGETS
	return target_dict

def checkValues():
	humidity = h.get_humidity()/100.0 # in %RH
	temperature = h.get_temperature()/100.0 # in °C
	uv = uvl.get_uv_light()/10.0 # in mW/m²
	sensor_data = getTargets()
	sensor_data["temperature"] = temperature
	sensor_data["humidity"] = humidity
	sensor_data["uv"] = uv
	sensor_data["timestamp"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	print(sensor_data)
	# ret = send(sensor_data)
	return

ipcon = IPConnection() # Create IP connection
h = BrickletHumidityV2(UID_H, ipcon) # Create humidity bricklet object
uvl = BrickletUVLight(UID_UV, ipcon) # Create uv bricklet object
ipcon.connect(HOST, PORT)

# Executes the checkValues function every x sencdons/minutes.
# Important: If the current checkValues execution is not finished the next one will be skipped.
# Maximum number of running instances = 1
scheduler = BlockingScheduler()
scheduler.add_job(checkValues, 'interval', seconds=10)
scheduler.start()

@api.resource("/targets")
class Command(Resource):
    
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument( "temprature_target", required=True, type = float)
		self.reqparse.add_argument( "humidity_target", required=True, type = float)
		self.reqparse.add_argument( "uv_target", required=True, type = float)
		super( Command, self).__init__()
    
	def get(self):
		return getTargets(), 200

	def post(self):
		self.args = self.reqparse.parse_args()
		db = shelve.open("targets", writeback=False)
		db["temprature_target"] = self.args["temprature_target"]
		db["humidity_target"] = self.args["humidity_target"]
		db["uv_target"] = self.args["uv_target"]
		db.close()
		return "ok", 200

if __name__ == '__main__':
	app.run()