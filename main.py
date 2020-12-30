from dogcamstreamer import DogCamStreamer
from dogcamaifactory import DogCamAIFactory
from dogcamsocket import DogCamSocket
from dogcamconfig import DogCamConfig
from dogcamlogger import DogCamLogger, DCLogLevel
import time

DogCamLogger.Start()
DogCamLogger.Log("Starting classes", DCLogLevel.Notice)

dcc = DogCamConfig()

aiUsed = dcc.AIMethod.lower()

dcai = DogCamAIFactory.CreateAI(aiType=aiUsed,
  aiModel=dcc.AIModels[aiUsed],
  boundsSize=dcc.AIBoundsSize,
  minimumConfidence=dcc.AIMinimumConfidence,
  displayOut=dcc.AIDisplayVision,
  detectionID=dcc.AIDetectID)

if dcai is None:
  DogCamLogger.Log("AI Project exiting due to failure to start AI", DCLogLevel.Notice)
  exit()

dcs = DogCamStreamer(dcc.StreamingURL,
  timeBetweenCaptures=dcc.StreamingCaptureRate,
  disconnectionTimeout=dcc.StreamingTimeout,
  frameBufferSize=dcc.StreamingFrameBufferSize)

dcso = DogCamSocket(dcc.CommandsAddress, MaxTimeout=dcc.CommandsTimeout)

DogCamLogger.Log("Starting command socket connection", DCLogLevel.Notice)
dcso.Connect()

if dcs.Start():
  dcs.Resize(newWidth=320, newHeight=240)
  dcai.SetDimensions(dcs.resWidth, dcs.resHeight)
  dcai.Start()

  DogCamLogger.Log("Starting main loop", DCLogLevel.Notice)
  while dcs.Running():
    dcai.PushImage(dcs.Read())

    while dcai.commandQueue.empty() is False:
      command = dcai.commandQueue.get_nowait()
      DogCamLogger.Log(f"Got command: {command}", DCLogLevel.Log)
      dcso.SendPosition(command)

    # Push info messages constantly.
    dcso.SendMessage(dcs.GetStatus())
    
    time.sleep(0.001)

DogCamLogger.Log("Ending AI controller", DCLogLevel.Notice)
dcs.Stop()
dcai.Stop()
dcso.Disconnect()
