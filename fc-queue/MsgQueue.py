import shelve
from threading import Lock
import traceback
'''
shelve is a standard library that allows storage of python dictionary
we store data as a dictionary and store the ids for preserving the order in the key `ids`
'''

class Queue():
    def __init__(self, filename, max_size):
        self.max_size = max_size
        self.filename = filename
        self.queue = shelve.open(filename, writeback=False)
        if not 'ids' in self.queue:
            self.queue['ids'] = []
    def insert(self, id, object):
        with self.mutex:
            db = shelve.open(self.filename, writeback=False)
            db['ids'].append(id)
            db[id] = object
            # if len(db['ids']) > self.max_size:
            #     self.pop(False)
    def get_first_element(self):
        with self.mutex:
            db = shelve.open(self.filename, writeback=False)
            retVal = None
            ids = db['ids']
            if len(ids) > 0:
                id = ids[0]
                if id in db:
                    retVal = db[id]
        return retVal
    def pop(self, withLock=True):
        if withLock:
            self.mutex.acquire()
        db = shelve.open(self.filename, writeback=False)
        retVal = None
        ids = db['ids']
        if len(ids) > 0:
            id = ids.pop(0)
            if id in db:
                retVal = db[id]
                del db[id]
        if withLock:
            self.mutex.release()
        return retVal
    def empty(self):
        print("empty")
        with self.mutex:
            db = shelve.open(self.filename, writeback=False)
        return len(db['ids']) == 0
        