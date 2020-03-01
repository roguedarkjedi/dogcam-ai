import cv2
import threading
import time

class DogCamStreamer():
  __cap: None
  __img: None
  __thread: None
  __lock: threading.Lock()
  
  __Running: False
  __Read: False
  __LastReadTime: 0
  __LastErrorTime: 0
  
  resWidth: 0
  resHeight: 0
  vidURL: ""
  
  def __init__(self, inURL):
    self.vidURL = inURL
  
  def Open(self):
    self.__cap = cv2.VideoCapture(self.vidURL)
    if not self.__cap.isOpened():
      print("Could not capture the video!")
      self.__cap = None
      return False
    
    self.resWidth, self.resHeight = self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH), self.__cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    return True
    
  def Start(self):
    if self.Open():
      print("Starting thread")
      self.__Running = True
      self.__thread = threading.Thread(target=self.__Update, daemon=True)
      self.__thread.start()
      return True

    return False
    
  def __Update(self):
    while self.__Running:
      retVal, image  = self.__cap.read()
      
      if not retVal:
        print("Detected error, waiting for fix")
        if self.__LastErrorTime == 0:
          self.__LastErrorTime = time.time()
          
        if time.time() - self.__LastErrorTime >= 10.0:
          print("Time out has occurred!")
          self.__Running = False
          break

      if self.__Read is True and time.time() - self.__LastReadTime >= 3.0:
        print("Capturing image")
        self.__lock.acquire(True)
        self.__img = image
        self.__Read = False
        self.__LastErrorTime = 0
        self.__LastReadTime = time.time()
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
    self.__thread.join()
    
    time.sleep(1)
    if self.__cap is not None:
      self.__cap.Release()
