import shelve
from threading import Lock
'''
shelve is a standard library that allows storage of python dictionary
we store data as a dictionary and store the ids for preserving the order in the key `ids`
'''

class Queue():
    def __init__(self, filename, max_size):
        self.max_size = max_size
        self.mutex = Lock()
        self.filename = filename
        self.queue = shelve.open(filename, writeback=False)
        self.queue.close()
        if not 'ids' in self.queue:
            self.queue['ids'] = []
    def insert(self, id, object):
        with self.mutex:
            self.queue['ids'].append(id)
            self.queue[id] = object
            if len(self.queue['ids']) > self.max_size:
                self.pop(False)
    def delete(self,id):
        with self.mutex:
            ids = self.queue['ids']
            if id in ids:
                self.queue.remove(id)
                self.queue['ids'] = ids
            if id in self.queue:
                del self.queue[id]
    def get_last_element(self):
        with self.mutex:
            retVal = None
            ids = self.queue['ids']
            if len(ids) > 0:
                id = ids[-1]
                if id in self.queue:
                    retVal = self.queue[id]
            self.mutex.release()
        return retVal
    def get_first_element(self):
        with self.mutex:
            retVal = None
            ids = self.queue['ids']
            if len(ids) > 0:
                id = ids[0]
                if id in self.queue:
                    retVal = self.queue[id]
        return retVal
    def get_ids(self):
        with self.mutex:
            ids = self.queue['ids'].copy()
            return ids
    def pop(self, withLock=True):
        if withLock:
            self.mutex.acquire()
        retVal = None
        ids = self.queue['ids']
        if len(ids) > 0:
            id = ids.pop(0)
            if id in self.queue:
                retVal = self.queue[id]
                del self.queue[id]
        if withLock:
            self.mutex.release()
        return retVal
    def dump(self):
        for key in self.queue:
            print(f"{key}: {self.queue[key]}")
    def empty(self):
        with self.mutex:
            return len(self.queue['ids']) == 0
    def close(self):
        self.queue.close()
        