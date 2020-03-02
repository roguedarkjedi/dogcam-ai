import cv2
import threading
import time

class DogCamStreamer():
  __cap = None
  __img = None
  __thread = None
  __lock = threading.RLock()
  
  __Running = False
  __LastReadTime = 0.0
  __LastErrorTime = 0.0
  
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
    print("Webstream: Loading video feed")
    self.__cap = cv2.VideoCapture(self.vidURL)
    if not self.__cap.isOpened():
      print("Webstream: Could not capture the video!")
      self.__cap = None
      return False
    
    if self.resWidth == 0:
      self.resWidth = self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    if self.resHeight == 0:
      self.resHeight = self.__cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return True
    
  def Start(self):
    if self.Open():
      print("Webstream: Starting thread")
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
  
  def __ReleaseCapture(self):
    if self.__cap is not None:
      self.__cap.release()
      self.__cap = None
      
  def __CheckTimeout(self):
    hasHitTimeout = (time.time() - self.__LastErrorTime) >= self.netTimeout and self.__LastErrorTime > 0.0
    if self.__cap is None or self.__cap.isOpened() is False or hasHitTimeout:
      if hasHitTimeout:
        print("Webstream: Timeout has occurred!")
        self.__Running = False
        self.__ReleaseCapture()
        self.__BlankImage()
        return False
      else:
        self.__SetError()
        self.Open()
        time.sleep(1)
    return True

  def __SetError(self):
    if self.__LastErrorTime <= 1.0:
      print("Webstream: Detected error, waiting...")
      self.__LastErrorTime = time.time()
      self.__BlankImage()
      self.__ReleaseCapture()
      
  def __BlankImage(self):
    print("Webstream: Blanking image")
    self.__lock.acquire()
    self.__img = None
    self.__lock.release()
    
  def __Update(self):
    while self.__Running:     
      if self.__CheckTimeout() is False:
        break
      
      if self.__cap is None:
        self.__SetError()
        continue

      retVal, image  = self.__cap.read()
      
      if not retVal:
        self.__SetError()
        continue
      elif (time.time() - self.__LastReadTime) >= self.captureRate:
        # If we cannot capture a lock, then don't capture the image
        if self.__lock.acquire(False) is False:
          continue
        print("Webstream: Capturing image")
        self.__img = cv2.resize(image, (self.resWidth, self.resHeight))
        self.__LastReadTime = time.time()
        self.__lock.release()
        if self.__LastErrorTime > 0.0:
          print("Webstream: Recovered from net disruption")
          self.__LastErrorTime = 0
  
  def Read(self):
    self.__lock.acquire(True)
    retImg = self.__img
    self.__lock.release()
    
    return retImg
  
  def Running(self):
    return self.__Running

  def Stop(self):
    self.__Running = False
    self.__BlankImage()
    
    if self.__thread is not None:
      self.__thread.join()

    self.__ReleaseCapture()
