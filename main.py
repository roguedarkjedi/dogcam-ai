from dogcamstreamer import DogCamStreamer
from dogcamai import DogCamAI
from dogcamsocket import DogCamSocket
from dogcamconfig import DogCamConfig

print("Starting classes")
dcc = DogCamConfig()
dcs = DogCamStreamer(dcc.StreamingURL, 
  timeBetweenCaptures=dcc.StreamingCaptureRate, 
  disconnectionTimeout=dcc.StreamingTimeout)
dcso = DogCamSocket(dcc.CommandsAddress)

dcai = DogCamAI(boundsSize=dcc.AIBoundsSize, 
  minimumConfidence=dcc.AIMinimumConfidence, 
  displayOut=dcc.AIDisplayVision)

print("Starting command socket connection")
dcso.Connect()

print("Loading video feed")
if dcs.Start():
  dcs.Resize(newWidth=300, newHeight=300)
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
