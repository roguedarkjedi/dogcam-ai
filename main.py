from dogcamstreamer import DogCamStreamer
from dogcamai import DogCamAI
import queue
import time

print("Starting streamer")
dcs = DogCamStreamer("rtmp://192.168.50.4/camera/g")
dcai = DogCamAI()

print("Loading feed")
if dcs.Start():
  dcai.SetDimensions(dcs.resWidth, dcs.resHeight)
  dcai.Start()
  
  print("Starting main loop")
  while True:
    dcai.PushImage(dcs.Read())
    
    while not dcai.commandQueue.empty():
      command = dcai.commandQueue.get_nowait()
      print(f"Got command: {command}")
      
dcs.Stop()
dcai.Stop()
