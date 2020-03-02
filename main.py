from dogcamstreamer import DogCamStreamer
from dogcamai import DogCamAI
from dogcamsocket import DogCamSocket

print("Starting classes")
dcs = DogCamStreamer("rtmp://192.168.50.4/camera/g")
dcso = DogCamSocket("ws://192.168.50.169:5867/")
dcai = DogCamAI()

print("Starting socket connection")
dcso.Connect()

print("Loading video feed")
if dcs.Start():
  dcs.Resize(0.5)
  dcai.SetDimensions(dcs.resWidth, dcs.resHeight)
  dcai.Start()
  
  print("Starting main loop")
  while True:
    dcai.PushImage(dcs.Read())
    
    while dcai.commandQueue.empty() is False:
      command = dcai.commandQueue.get_nowait()
      print(f"Got command: {command}")
      dcso.SendPosition(command)
      
dcs.Stop()
dcai.Stop()
dcso.Disconnect()
