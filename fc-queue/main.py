from concurrent.futures import thread
import shelve
import queue
from time import sleep, perf_counter
from flask import Flask
from flask_restful import Resource, Api, reqparse
from threading import Thread, Lock
from random import randrange
from request import *
import datetime

app = Flask("CloudQueue")
api = Api(app)

incoming_queue = queue.Queue(0)
incoming_lock = Lock()
outgoing_queue = queue.Queue(0)

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
    global incoming_queue
    wait = 0
    while True:
        if wait > 0:
            sleep(wait)
        if not incoming_queue.empty():
            incoming_lock.acquire()
            item = incoming_queue.get()
            ret , success = send(item)
            if success:
                wait = 0
                outgoing_queue.put(ret)
            else:
                incoming_queue = copyQueue( incoming_queue, ret)
                wait = wait + 10
            incoming_lock.release()
        else:
            sleep(5)

def copyQueue(copy_queue, first_item=False):
	new_queue = queue.Queue(0)
	if not first_item == False:
		new_queue.put(first_item)
	while not copy_queue.empty():
		item = copy_queue.get()
		if datetime.datetime.strptime(item["timestamp"], '%Y-%m-%d %H:%M:%S') > datetime.datetime.now()-datetime.timedelta(minutes=30):
			new_queue.put(item)
	return new_queue

inc_thread = Thread(target=check_inc)
inc_thread.start()

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
        self.reqparse.add_argument( "timestamp", required=True, type = str)
        super( Command, self).__init__()
    
    def post(self):
        self.args = self.reqparse.parse_args()
        incoming_lock.acquire()
        incoming_queue.put(self.args)
        incoming_lock.release()
        return  "ok", 200
    
    def get(self):
        if not outgoing_queue.empty():
            return outgoing_queue.get(), 200
        else:
            return {}, 404

if __name__ == '__main__':
    app.run(Threaded=True)