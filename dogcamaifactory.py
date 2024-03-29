from dogcamlogger import DogCamLogger, DCLogLevel
from dogcamai_tflite import DogCamAITFLite
from dogcamai_dnn import DogCamAIDNN
from os import path

class DogCamAIFactory():

  @staticmethod
  def CreateAI(aiType, aiModel, boundsXSize=10, boundsYSize=10, minimumConfidence=0.3, displayOut=False,
                detectionID=0, logMatches=False, throttleTilt=False, tiltCooldown=0.75):
    NewAIClass = None

    DogCamLogger.Log(f"AI: Using model file {aiModel}", DCLogLevel.Verbose)

    if not path.exists(aiModel):
      DogCamLogger.Log(f"AI: Given model file {aiModel} does not exist!", DCLogLevel.Error)
      return None

    className = aiType
    if className == "tf":
      NewAIClass = DogCamAITFLite(aiModel)
    elif className == "dnn":
      NewAIClass = DogCamAIDNN(aiModel)

    if NewAIClass is not None:
      NewAIClass.Initialize(boundsXSize, boundsYSize, minimumConfidence, displayOut, detectionID, logMatches, throttleTilt, tiltCooldown)
    else:
      DogCamLogger.Log(f"AI: Could not create class of type {className}! Fatal error!",
                DCLogLevel.Error)

    return NewAIClass
