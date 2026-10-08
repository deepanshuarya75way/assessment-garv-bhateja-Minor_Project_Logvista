import time

class LiveLogMonitor:
  def __init__(self, file_path):
    self.file_path = file_path
    self.running = False
  def start(self,callback):
    self.running = True
    with open(self.file_path,"r",encoding="utf-8") as file:
      file.seek(0, 2)
      while self.running:
        line= file.readline()

        if line:
          callback(line.strip())
        else:
          time.sleep(0.5)
  def stop(self):
    self.running = False