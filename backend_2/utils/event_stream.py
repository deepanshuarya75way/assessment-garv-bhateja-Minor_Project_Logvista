import queue
import json

subscribers=[]

def subscribe():
  client_queue=queue.Queue()
  subscribers.append(client_queue)
  print("SSE Subscriber added")
  print("total subscribers:",len(subscribers))      
  return client_queue

def unsubscribe(client_queue):
  if client_queue in subscribers:
    subscribers.remove(client_queue)
    print("SSE Subscriber removed")
    print("total subscribers:",len(subscribers))

def generate_events(client_queue):
  while True:
    event=client_queue.get()
    print("sending sse event:",event)
    yield f"Data: {json.dumps(event)}\n\n"

def publish(event):
  print("publishiing event:", event)
  print("subscribers:",len(subscribers))
  for client_queue in subscribers:
    client_queue.put(event)