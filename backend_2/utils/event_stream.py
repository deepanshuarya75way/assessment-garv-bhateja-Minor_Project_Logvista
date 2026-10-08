import queue
import json

subscribers=[]

def subscribe():
  q=queue.Queue()
  subscribers.append(q)
  return q

def unsubscribe(q):
  if q in subscribers:
    subscribers.remove(q)

def generate_events(client_queue):
  while True:
    event=client_queue.get()
    yield f"Data: {json.dumps(event)}\n\n"

def publish(event):
  for q in subscribers:
    q.put(event)