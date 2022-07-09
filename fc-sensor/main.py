from apscheduler.schedulers.background import BlockingScheduler
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_humidity_v2 import BrickletHumidityV2
from tinkerforge.bricklet_uv_light import BrickletUVLight
import time

HOST = "host.docker.internal"
# HOST = "localhost"
PORT = 4223
UID_H = "HF1" # UID of Humidity Bricklet 2.0
UID_UV = "xkb" # UID of UV Light Bricklet


def checkValues():
	humidity = h.get_humidity()/100.0 # in %RH
	temperature = h.get_temperature()/100.0 # in °C
	uv = uvl.get_uv_light()/10.0 # in mW/m²
	print(humidity)
	print(temperature)
	print(uv)
	return

if __name__ == "__main__":
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