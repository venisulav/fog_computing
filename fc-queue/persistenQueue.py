import pickle
import queue
from threading import Lock
"""
Persistent queue class extends the standard, threadsafe python queue implementation.
Each queue now has a pickle file. When the queue is changed with put, the changes are saved to the pickle file.
Additionally, a new function 'peek' is introduced, that returns the first item without deleting it from the queue.
Note: Two different PersistentQueue objects should never use the same pickle file.
"""
# TODO: test if a thread can acquire the same lock twice (so if it has already acquired it) or if it will block.
class PersistentQueue(queue.Queue):
    
    def __init__(self, name, maxsize):
        self.maxsize = maxsize
        self.Lock = Lock()
        self.persistentFile = f"./pickle/{name}.pkl"
        super(PersistentQueue, self).__init__(maxsize)
        try:
            self.restore()
        except:
            pass
        
    def put(self, item):
        with self.Lock:
            super(PersistentQueue, self).put(item)
            self.save()
            
    def get(self):
        with self.Lock:
            item = super(PersistentQueue, self).get()
            self.save()
        return item
    
    def peek(self):
        with self.Lock:
            item = super(PersistentQueue, self).get()
            self.restore()
        return item
            
    def save(self):
        with open(self.persistentFile, 'wb') as f:
                pickle.dump(self.queue, f)
         
    # TODO: consider cleaner implementation of restore       
    def restore(self):
        # super(PersistentQueue, self).__init__(self.maxsize)
        with open(self.persistentFile, 'rb') as f:
                self.queue = pickle.load(f)