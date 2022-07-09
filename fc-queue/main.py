from concurrent.futures import thread
import shelve
from time import sleep, perf_counter
from flask import Flask
from flask_restful import Resource, Api, reqparse
from threading import Thread, Lock
from random import randrange
from request import *
from config import *
from MsgQueue import *

app = Flask("CloudQueue")
api = Api(app)

# incoming_queue = queue.Queue(0)
incoming_lock = Lock()
incoming_queue = Queue("inc_queue", MAX_QUEUE_SIZE)
# outgoing_queue = Queue(0)

"""
Idea: 
    A persistent message queue. The message queue will accent incoming requests. 
    This can perhaps be done with flask app.run(threded=True), however it needs to be tested.
    The message queue will have 2 types of workers running the background.
        1. Relayer - Will check the incoming queue. If necessary dequeue and pass on to the backend.
            Response -> outgoing MQ.
        2. Responder - Checks outgoing MQ and sends response.

TODO:
	- check if flask allows threads to run in the background
    - How to handle scalability??? 
"""
# create thread sage queues
"""
Idea: Queue-Flip-Flop
    If the backend is not availiable to receive the queue item the current queue item needs to remain in the first position.
    For that case there will be two queues. The current item will be placed at the begining of the queue.
    The other items will then be moved from one queue to the other.
    
    
    
    What is the current problem?
        If the backend is not available, then we will have to attempt to flip-flip the queue. 
        However in the mean time new requests could be arriving. This would make flip-flopping the queue really hard.
        
        How to solve this problem:
            1. ZeroMQ: 
            2. Try to lock the queue somehow
"""

def check_inc():
    # global incoming_queue
    wait = 0
    while True:
        if wait > 0:
            sleep(wait)
        incoming_lock.acquire()
        if not incoming_queue.empty():
            print("Got something!")
            item = incoming_queue.get_first_element()
            ret , success = send(item)
            if success:
                wait = 0
                incoming_queue.pop()
                print("On to the next one :D")
                print(ret)
        else:
            sleep(5)
        incoming_lock.release()

# def flip_flop(copy_queue, first_item):
#     new_queue = queue.Queue(0)
#     new_queue.put(first_item)
#     while not copy_queue.empty():
#         new_queue.put(copy_queue.get())
#     return new_queue, copy_queue

inc_thread = Thread(target=check_inc)
inc_thread.start()

# thread_list = []
# for i in range(3):
#     thread = Thread(target=checkInc, args=(i,))
#     thread_list.append(thread)
#     thread.start()
    

# thread1 = Thread(task,args=)
# thread2 = Thread(task,args=args_tuple)

@api.resource("/queue")
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
    
    def post(self):
        self.args = self.reqparse.parse_args()
        incoming_lock.acquire()
        print("App got lock.")
        incoming_queue.insert("hi", self.args)
        incoming_lock.release()
        print("App released lock.")
        return  "ok", 200
    
    
	# def get(self):
	# 	self.args = self.reqparse.parse_args()
	# 	self.weather , self.windAlert = getWeather( self.args["lat"], self.args["lon"])
	# 	return self.getSettings()

	# def getSettings(self):
	# 	heater, ac, window = self.tempratureSetting()
	# 	humidifier, dehumidifier = self.humiditySetting(window)
	# 	uvLight, blinds= self.uvSetting()
	# 	command = {
	# 		"heater": heater,
	# 		"ac": ac,
	# 		"window": window,
	# 		"humidifier": humidifier,
	# 		"dehumidifier": dehumidifier,
	# 		"uvLight": uvLight,
	# 		"blinds": blinds,
	# 	}
	# 	return command, 200

	# def tempratureSetting(self):
	# 	"""
	# 	Use outside, measured, and target temprature to respond with optimised command.
	# 	Aritificial Reulgation:
	# 		Target > Temp:
	# 			Turn on heater
	# 		Target < Temp:
	# 			Turn on AC
	# 		Else:
	# 			Turn off AC and heater
	# 	Wind Alert == False:
	# 		Window Regulation:
	# 			Target > Temp && Out_Temp > Target:
	# 				Turn off heater & ac
	# 				Open window
	# 			Target < Temp && Out_Temp < Target:
	# 				Turn off ac & heater
	# 				Open window
	# 			Else:
	# 				Do nothing
	# 	Return heater, ac, window
	# 	"""
	# 	# TODO: consider rain
	# 	# Artificial regulation
	# 	heater = False
	# 	ac = False
	# 	window = False
	# 	if self.args["temprature_target"] > self.args["temprature"]:
	# 		heater = True
	# 	elif self.args["temprature_target"] < self.args["temprature"]:
	# 		ac = True
	# 	if self.windAlert == False:
	# 		# Window regulation
	# 		if self.args["temprature_target"] > self.args["temprature"] and self.weather["temprature"] > self.args["temprature_target"]:
	# 			heater = False
	# 			window = True
	# 		elif self.args["temprature_target"] < self.args["temprature"] and self.weather["temprature"] < self.args["temprature_target"]:
	# 			ac = False
	# 			window = True	
	# 	return heater, ac, window

	# def humiditySetting(self, window):
	# 	"""
	# 	Use outside, measured, and target humidity to give optimal command.
	# 	Temprature is given precendence over humidity. If the window is open, then the humidifier and de-humidifier will remain off.
	# 	Window == False
	# 		Target > Humidity:
	# 			Turn on humidifier
	# 		Target < Humidity:
	# 			Turn on dehumidifier (if availiable)
	# 		Else:
	# 			Do nothing
	# 	Return humidifier, dehumidifier
	# 	"""
	# 	# TODO: consider outside humidity
	# 	humidifier = False
	# 	dehumidifier = False
	# 	if window == False:
	# 		if self.args["humidity_target"] > self.args["humidity"]:
	# 			humidifier = True
	# 		elif self.args["humidity_target"] < self.args["humidity"]:
	# 			dehumidifier = True
	# 	return humidifier, dehumidifier

	# def uvSetting(self):
	# 	"""
	# 	Check uv target and measured values. Also consider weather conditions.
	# 	"""
	# 	# TODO: figure out what a maximum value could be and 
	# 	blinds = 0
	# 	uvLight = False
	# 	return uvLight, blinds

if __name__ == '__main__':
    
    app.run(Threaded=True)