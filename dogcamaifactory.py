from dogcamlogger import DogCamLogger, DCLogLevel
from dogcamai_tflite import DogCamAITFLite
from dogcamai_dnn import DogCamAIDNN

class DogCamAIFactory():

  @staticmethod
  def CreateAI(aiType, boundsSize=100, minimumConfidence=0.3, displayOut=False,
                detectionID=0, fpsSync=0):
    NewAIClass = None

    className = aiType.lower()
    if className == "tf":
      NewAIClass = DogCamAITFLite()
    elif className == "dnn":
      NewAIClass = DogCamAIDNN()

    if NewAIClass is not None:
      NewAIClass.Initialize(boundsSize, minimumConfidence, displayOut, detectionID, fpsSync)
    else:
      DogCamLogger.Log(f"AI: Could not create class of type {className}! Fatal error!",
                DCLogLevel.Error)

    return NewAIClass
