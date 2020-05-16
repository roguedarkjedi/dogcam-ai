from dogcamstreamer import DogCamStreamer
from dogcamai import DogCamAI
from dogcamsocket import DogCamSocket
from dogcamconfig import DogCamConfig
from dogcamlogger import DogCamLogger, DCLogLevel
import time

DogCamLogger.Start()
DogCamLogger.Log("Starting classes", DCLogLevel.Notice)

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

DogCamLogger.Log("Starting command socket connection", DCLogLevel.Notice)
dcso.Connect()

if dcs.Start():
  dcs.Resize(newWidth=300, newHeight=300)
  dcai.SetDimensions(dcs.resWidth, dcs.resHeight)
  dcai.Start()

  DogCamLogger.Log("Starting main loop", DCLogLevel.Notice)
  while dcs.Running():
    dcai.PushImage(dcs.Read())

    while dcai.commandQueue.empty() is False:
      command = dcai.commandQueue.get_nowait()
      DogCamLogger.Log(f"Got command: {command}", DCLogLevel.Debug)
      dcso.SendPosition(command)

    time.sleep(0.1)

DogCamLogger.Log("Ending AI controller", DCLogLevel.Notice)
dcs.Stop()
dcai.Stop()
dcso.Disconnect()
