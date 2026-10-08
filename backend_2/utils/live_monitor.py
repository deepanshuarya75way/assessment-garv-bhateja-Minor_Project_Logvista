import time

class LiveLogMonitor:
  def __init__(self, file_path,callback):
    self.file_path = file_path
    self.callback=callback
    self.running = False
  def start(self):
    self.running = True
    print("LIVE MONITOR STARTED")
    print("WATCHING:",self.file_path)
    try:
      with open(self.file_path,"r",encoding="utf-8",errors="ignore") as file:
        file.seek(0, 2)
        while self.running:
          line= file.readline()

          if line:
            line=line.strip()
            if line:
              print("New line:",line)
              self.callback(line)
          else:
            time.sleep(0.3)
    except Exception as e:
      print("Live MONITOR ERROR:",e)
      
  def stop(self):
    self.running = False