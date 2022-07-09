from MsgQueue import *

queue = Queue("test",10)

queue.insert("hi", {"hi":100})
queue.dump()