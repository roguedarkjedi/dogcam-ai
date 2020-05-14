from dogcamstreamer import DogCamStreamer
from dogcamai import DogCamAI
from dogcamsocket import DogCamSocket
from dogcamconfig import DogCamConfig

print("Starting classes")

dcc = DogCamConfig()
dcs = DogCamStreamer(dcc.StreamingURL,
  timeBetweenCaptures=dcc.StreamingCaptureRate,
  disconnectionTimeout=dcc.StreamingTimeout,
  frameBufferSize=dcc.StreamingFrameBufferSize,
  videoFPS=dcc.StreamingFPS)

dcso = DogCamSocket(dcc.CommandsAddress, MaxTimeout=dcc.CommandsTimeout)

dcai = DogCamAI(boundsSize=dcc.AIBoundsSize,
  minimumConfidence=dcc.AIMinimumConfidence,
  displayOut=dcc.AIDisplayVision,
  detectionID=dcc.AIDetectID,
  fpsSync=dcc.StreamingFPS)

print("Starting command socket connection")
dcso.Connect()

if dcs.Start():
  dcs.Resize(newWidth=300, newHeight=300)
  dcai.SetDimensions(dcs.resWidth, dcs.resHeight)
  dcai.Start()

  print("Starting main loop")
  while dcs.Running():
    dcai.PushImage(dcs.Read())

    while dcai.commandQueue.empty() is False:
      command = dcai.commandQueue.get_nowait()
      print(f"Got command: {command}")
      dcso.SendPosition(command)

print("Ending AI controller")
dcs.Stop()
dcai.Stop()
dcso.Disconnect()
