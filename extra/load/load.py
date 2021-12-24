import os
import time

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

class Loader:
  def __init__(self):
    self.first = False
    self.i = 0
    self.state = "initializing loader..."
    self.on = False
  
  def next(self, msg):
    self.on = True
    self.state = msg
    while self.on:
      self.writeMsg(msg)
  
  def writeMsg(self, msg):
    if not self.first:
      self.first = False
      time.sleep(0.5)
    self.i += 1
    if self.i >= 4:
      self.i = 0
    cls()
    print(msg)
    for x in range(self.i):
      print('.', end='')
  
  def stop(self):
    self.on = False