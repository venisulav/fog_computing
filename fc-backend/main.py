from xmlrpc.client import Boolean
from flask import Flask
from flask_restful import Resource, Api, reqparse
from weather import getWeather

app = Flask("TempBackend")
api = Api(app)

"""
Idea: 
	A simple stateless backend. The backend will wait for datapoints.
	Once it receives a datapoint it will use weather data to issue a command and send it.
	Even though this project was intended to be a RESTful service it probably does not need to be.

Requirements
	1. The app should accept data from the edge.
	2. The app should get local weather data.
	3. The app should use the collected and supplied weather data to issue an ideal command.

TODO:
	- check other TODOs in files
	- fault tolerance
"""

@api.resource("/cmd")
class Command(Resource):
    
	def __init__(self):
		self.reqparse = reqparse.RequestParser()
		self.reqparse.add_argument( "temprature", required=True, type = float)
		self.reqparse.add_argument( "temprature_target", required=True, type = float)
		self.reqparse.add_argument( "humidity", required=True, type = float)
		self.reqparse.add_argument( "humidity_target", required=True, type = float)
		self.reqparse.add_argument( "uv", required=True, type = float)
		self.reqparse.add_argument( "uv_target", required=True, type = float)
		self.reqparse.add_argument( "lon", required=True, type = float)
		self.reqparse.add_argument( "lat", required=True, type = float)
		super( Command, self).__init__()
    
	def get(self):
		self.args = self.reqparse.parse_args()
		self.weather , self.windAlert = getWeather( self.args["lat"], self.args["lon"])
		return self.getSettings()

	def getSettings(self):
		heater, ac, window = self.tempratureSetting()
		humidifier, dehumidifier = self.humiditySetting(window)
		uvLight, blinds= self.uvSetting()
		command = {
			"heater": heater,
			"ac": ac,
			"window": window,
			"humidifier": humidifier,
			"dehumidifier": dehumidifier,
			"uvLight": uvLight,
			"blinds": blinds,
		}
		return command, 200

	def tempratureSetting(self):
		"""
		Use outside, measured, and target temprature to respond with optimised command.
		Aritificial Reulgation:
			Target > Temp:
				Turn on heater
			Target < Temp:
				Turn on AC
			Else:
				Turn off AC and heater
		Wind Alert == False:
			Window Regulation:
				Target > Temp && Out_Temp > Target:
					Turn off heater & ac
					Open window
				Target < Temp && Out_Temp < Target:
					Turn off ac & heater
					Open window
				Else:
					Do nothing
		Return heater, ac, window
		"""
		# TODO: consider rain
		# Artificial regulation
		heater = False
		ac = False
		window = False
		if self.args["temprature_target"] > self.args["temprature"]:
			heater = True
		elif self.args["temprature_target"] < self.args["temprature"]:
			ac = True
		if self.windAlert == False:
			# Window regulation
			if self.args["temprature_target"] > self.args["temprature"] and self.weather["temprature"] > self.args["temprature_target"]:
				heater = False
				window = True
			elif self.args["temprature_target"] < self.args["temprature"] and self.weather["temprature"] < self.args["temprature_target"]:
				ac = False
				window = True	
		return heater, ac, window

	def humiditySetting(self, window):
		"""
		Use outside, measured, and target humidity to give optimal command.
		Temprature is given precendence over humidity. If the window is open, then the humidifier and de-humidifier will remain off.
		Window == False
			Target > Humidity:
				Turn on humidifier
			Target < Humidity:
				Turn on dehumidifier (if availiable)
			Else:
				Do nothing
		Return humidifier, dehumidifier
		"""
		# TODO: consider outside humidity
		humidifier = False
		dehumidifier = False
		if window == False:
			if self.args["humidity_target"] > self.args["humidity"]:
				humidifier = True
			elif self.args["humidity_target"] < self.args["humidity"]:
				dehumidifier = True
		return humidifier, dehumidifier

	def uvSetting(self):
		"""
		Check uv target and measured values. Also consider weather conditions.
		"""
		# TODO: figure out what a maximum value could be and 
		blinds = 0
		uvLight = False
		return uvLight, blinds

if __name__ == '__main__':
    app.run(threaded=True, port=5001)