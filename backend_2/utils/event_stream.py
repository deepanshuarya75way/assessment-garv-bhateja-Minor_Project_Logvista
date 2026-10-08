import queue

subscribers=[]

def subscribe():
  q=queue.Queue()
  subscribers.append(q)
  return q

def unsubscribe(q):
  if q in subscribers:
    subscribers.remove(q)

def publish(event):
  for q in subscribers:
    q.put(event)