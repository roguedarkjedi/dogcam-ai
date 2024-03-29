from dogcamstreamer import DogCamStreamer
from dogcamaifactory import DogCamAIFactory
from dogcamsocket import DogCamSocket
from dogcamconfig import DogCamConfig
from dogcamlogger import DogCamLogger, DCLogLevel
from pathlib import Path
import time
import os

# Remove any handles before we start
if os.path.exists('exit_handle'):
  os.remove('exit_handle')

# Start AI stuff
DogCamLogger.Start()
DogCamLogger.Log("Starting classes", DCLogLevel.Notice)

exit_handle = Path('exit_handle')

dcc = DogCamConfig()

aiUsed = dcc.AIMethod.lower()

dcai = DogCamAIFactory.CreateAI(aiType=aiUsed,
  aiModel=dcc.AIModels[aiUsed],
  boundsXSize=dcc.AIBoundsXSize,
  boundsYSize=dcc.AIBoundsYSize,
  minimumConfidence=dcc.AIMinimumConfidence,
  displayOut=dcc.AIDisplayVision,
  detectionID=dcc.AIDetectID,
  logMatches=dcc.AILogMatches,
  throttleTilt=dcc.AIThrottleTilt,
  tiltCooldown=dcc.AITiltCooldown)

if dcai is None:
  DogCamLogger.Log("AI Project exiting due to failure to start AI", DCLogLevel.Error)
  exit()

dcs = DogCamStreamer(dcc.StreamingURL,
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
      if dcc.AILogMatches is True:
        DogCamLogger.Log(f"Got command: {command}", DCLogLevel.Log)
      dcso.SendPosition(command)

    # Push info messages constantly.
    dcso.SendMessage(dcs.GetStatus())

    time.sleep(0.001)

    # Check to see if we have an interrupt file/handle fired
    if exit_handle.exists():
       DogCamLogger.Log("Exit handle exists, stopping execution", DCLogLevel.Notice)
       break

DogCamLogger.Log("Ending AI controller", DCLogLevel.Notice)
dcs.Stop()
dcai.Stop()
dcso.Disconnect()
