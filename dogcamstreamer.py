import cv2
import threading
import time

class DogCamStreamer():
  __cap = None
  __img = None
  __thread = None
  __lock = threading.RLock()
  
  __Running = False
  __Read = True
  __LastReadTime = 0
  __LastErrorTime = 0
  
  resWidth = 0
  resHeight = 0
  vidURL = ""
  captureRate=0.0
  netTimeout=0.0
  
  def __init__(self, inURL, timeBetweenCaptures=5.0, disconnectionTimeout=10.0):
    self.vidURL = inURL
    self.captureRate = timeBetweenCaptures
    self.netTimeout = disconnectionTimeout
  
  def Open(self):
    self.__cap = cv2.VideoCapture(self.vidURL)
    if not self.__cap.isOpened():
      print("Could not capture the video!")
      self.__cap = None
      return False
    
    self.resWidth = self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    self.resHeight = self.__cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return True
    
  def Start(self):
    if self.Open():
      print("Starting thread")
      self.__Running = True
      self.__thread = threading.Thread(target=self.__Update, daemon=True)
      self.__thread.start()
      return True

    return False
    
  def Resize(self, percentage=1.0, newWidth=0, newHeight=0):
    if newWidth != 0:
      self.resWidth = newWidth
    else:
      self.resWidth = int(self.resWidth * percentage)
    
    if newHeight != 0:
      self.resHeight = newHeight
    else:
      self.resHeight = int(self.resHeight *percentage)
    
  def __Update(self):
    while self.__Running:
      retVal, image  = self.__cap.read()
      
      if not retVal:
        print("Detected error, waiting for fix")
        if self.__LastErrorTime == 0:
          self.__LastErrorTime = time.time()
          
        if (time.time() - self.__LastErrorTime) >= self.netTimeout:
          print("Time out has occurred!")
          self.__Running = False
          break

      if self.__Read is True and (time.time() - self.__LastReadTime) >= self.captureRate:
        print("Capturing image")
        self.__lock.acquire()
        self.__img = cv2.resize(image, (self.resWidth, self.resHeight))
        self.__Read = False
        self.__LastReadTime = time.time()
        self.__LastErrorTime = 0
        self.__lock.release()
  
  def Read(self):
    self.__lock.acquire(True)
    retImg = self.__img
    self.__lock.release()
    
    if retImg is not None:
      self.__Read = True
    
    return retImg
  
  def Stop(self):
    self.__Running = False
    
    if self.__thread is not None:
      self.__thread.join()

    if self.__cap is not None:
      self.__cap.Release()
