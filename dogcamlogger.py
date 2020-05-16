from enum import IntEnum, auto
from colorama import Fore, Style, init
import time
import datetime

__all__ = ["DCLogLevel", "DogCamLogger"]

class DCLogLevel(IntEnum):
  Debug=auto()
  Verbose=auto()
  Log=auto()
  Warn=auto()
  Error=auto()
  Notice=auto()
  Silence=auto()
  
  def __lt__(self, other):
    if self.__class__ is other.__class__:
      return self.value < other.value
    return NotImplemented
    
  @staticmethod
  def GetLevel(ForStr: str):
    try:
      return DCLogLevel[ForStr]
    except KeyError:
      return DCLogLevel.Log
      
  def ToString(self):
    return self.name
    
CurrentLoggingLevel = DCLogLevel.Log

class DogCamLogger():
  @staticmethod
  def Start():
    init()

  @staticmethod
  def GetTimestamp():
    return time.time()
    
  @staticmethod
  def PrintDate():
    NowTime = str(datetime.datetime.now())
    return f"[{NowTime}] "

  @staticmethod
  def Log(Input:str, LogLevel:DCLogLevel=DCLogLevel.Log, MakeBold:bool=False, MakeDim:bool=False):
    if LogLevel < CurrentLoggingLevel:
      return
      
    # Set up color logging
    ColorStr = ""
    if LogLevel == DCLogLevel.Error:
      ColorStr = Fore.RED + Style.BRIGHT
    elif LogLevel == DCLogLevel.Warn:
      ColorStr = Fore.YELLOW + Style.BRIGHT
    elif LogLevel == DCLogLevel.Verbose:
      ColorStr = Style.DIM
    elif LogLevel == DCLogLevel.Debug:
      ColorStr = Style.BRIGHT + Fore.BLACK
    elif LogLevel == DCLogLevel.Notice:
      ColorStr = Fore.GREEN + Style.BRIGHT
      
    if MakeBold is True:
      ColorStr += Style.BRIGHT
    elif MakeDim is True:
      ColorStr += Style.DIM
      
    print(DogCamLogger.PrintDate() + f"DogCamAI:{ColorStr} {Input}" + Style.RESET_ALL)
      
