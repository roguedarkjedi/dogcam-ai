from dogcamlogger import DogCamLogger, DCLogLevel
import json

class DogCamConfig():

  def __init__(self):
    with open("./config.json","r") as cfg_file:
      ConfigData = json.load(cfg_file)
      self.__dict__ = ConfigData
      DogCamLogger.SetLogLevel(self.LoggingLevel)
      DogCamLogger.Log("Config data has been loaded!", DCLogLevel.Notice)
