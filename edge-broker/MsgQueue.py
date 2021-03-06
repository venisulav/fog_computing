import shelve
from threading import Lock
from datetime import datetime
'''
shelve is a standard library that allows storage of python dictionary
we store data as a dictionary and store the ids for preserving the order in the key `ids`
'''

class Queue():
    def __init__(self, filename, max_size):
        self.max_size = max_size
        self.mutex = Lock()
        self.queue = shelve.open(filename, writeback=False)
        if not 'ids' in self.queue:
            self.queue['ids'] = []
    # should be called with lock
    def can_be_inserted(self, ts):
        ids = self.queue['ids']
        if len(ids) > 0:
            latest_str_ts = self.queue[ids[-1]]['timestamp']
            latest_ts = datetime.strptime(latest_str_ts,"%Y-%m-%d %H:%M:%S")
            return datetime.strptime(ts,"%Y-%m-%d %H:%M:%S") > latest_ts
        return True
    def insert(self, id, object):
        with self.mutex:
            if self.can_be_inserted(id) == False:
                return
            id_list = self.queue['ids']
            id_list.append(id)
            self.queue['ids'] = id_list
            object['sent'] = False
            self.queue[id] = object
            if len(self.queue['ids']) > self.max_size:
                self.pop(False)
    def delete(self,id):
        with self.mutex:
            ids = self.queue['ids']
            if id in ids:
                ids.remove(id)
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
            self.queue['ids']=ids
            if id in self.queue:
                retVal = self.queue[id]
                del self.queue[id]
                del retVal["sent"]
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
    def mark_as_sent(self, id):
        with self.mutex:
            if id in self.queue:
                self.queue[id]["sent"] = True
    def get_not_sent(self):
        with self.mutex:
            for id in self.queue["ids"]:
                if id in self.queue and self.queue[id]["sent"] == False:
                    return self.queue[id]

        