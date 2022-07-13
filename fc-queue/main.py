from concurrent.futures import thread
import shelve
import queue
from time import sleep, perf_counter
from flask import Flask
from flask_restful import Resource, Api, reqparse
from threading import Thread, Lock
from random import randrange
from request import *
from persistenQueue import *
import datetime
import sys
import pickle

app = Flask("CloudQueue")
api = Api(app)

incoming_queue = PersistentQueue("incoming_queue",0)
outgoing_queue = PersistentQueue("outgoing_queue",0)
timestamp_file = "./pickle/last_received_timestamp.pkl"
timestamp_lock = Lock()
  
# Try to load newest received timestamp. If none is found initialse to -10 years.  
def load_timestamp():
    try:
        with open(timestamp_file, 'rb') as f:
            ret =  pickle.load(f)
    except:
        ret = datetime.datetime.now() - datetime.timedelta(days=3600)
    return ret

last_received_timestamp = load_timestamp() 
print(last_received_timestamp)

# Used by inc_thread to check the queue for new items and pass theses on to the backend.
def check_inc():
    global incoming_queue
    wait = 0
    while True:
        if wait > 0:
            sleep(wait)
        if not incoming_queue.empty():
            item = incoming_queue.peek()
            current_timestamp = datetime.datetime.strptime(item["timestamp"], '%Y-%m-%d %H:%M:%S')
            if current_timestamp < datetime.datetime.now()-datetime.timedelta(minutes=30):
                incoming_queue.get()
                continue
            ret , success = send(item)
            if success:
                incoming_queue.get()
                outgoing_queue.put(ret)
                wait = 0
            else:
                if wait < 100:
                    wait = wait + 5
        else:
            sleep(5)

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
        global last_received_timestamp
        self.args = self.reqparse.parse_args()
        timestamp_lock.acquire()
        current_timestamp = datetime.datetime.strptime(self.args["timestamp"], '%Y-%m-%d %H:%M:%S')
        if current_timestamp >= last_received_timestamp:
            last_received_timestamp = current_timestamp
            with open(timestamp_file, 'wb') as f:
                pickle.dump(last_received_timestamp, f)
            incoming_queue.put(self.args)
            timestamp_lock.release()
            return  "Ok.", 200
        else:
            timestamp_lock.release()
            return "Rejected because newer data was already received.", 409
    
    def get(self):
        if not outgoing_queue.empty():
            return outgoing_queue.get(), 200
        else:
            return {}, 404

if __name__ == '__main__':
    app.run(Threaded=True)