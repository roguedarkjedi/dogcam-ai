import cv2
import numpy as np
import threading
import time
import queue

DOG = 18

class DogCamAI():
  net = None
  width = 0
  height = 0
  bounds = 0
  mConfidence = 0
  mThreshold = 0
  RunningThread = False
  debugDisplay = False
  
  commandQueue = queue.Queue()
  
  __thread = None
  __image = None
  __lock = threading.Lock()
  
  def __init__(self, boundsSize=100, minimumConfidence=0.3, displayOut=False):
    #self.net = cv2.dnn.readNetFromDarknet("./training/coco-tiny.cfg", "./training/coco-tiny.weights")
    self.net = cv2.dnn.readNetFromTensorflow("./training/mobilenet.pb", "./training/mobilenet.pbtxt")
    self.bounds = int(boundsSize)
    self.debugDisplay = displayOut
    self.mConfidence = float(minimumConfidence)
    self.__image = None

    self.__thread = threading.Thread(target=self.__Update)
  
  def SetDimensions(self, W, H):
    self.width = int(W)
    self.height = int(H)
    print(f"Resolution is {self.width}x{self.height}")
    
  def PushImage(self, image):
    if self.__lock.acquire(False) is False:
      return
    
    if self.__image is None and image is not None:
      print("Got image to process")
      self.__image = image
    self.__lock.release()
  
  def __Update(self):
    # Create Debug window
    if self.debugDisplay:
      cv2.startWindowThread()
      cv2.namedWindow("Output", cv2.WINDOW_NORMAL)
      cv2.resizeWindow("Output", (320, 240))
    
    while self.RunningThread:
      if self.__image is not None:
        self.__lock.acquire()
        self.__ProcessImage(self.__image)
        self.__image = None
        self.__lock.release()
      
      if self.debugDisplay:
        cv2.waitKey(1)

      time.sleep(0.3)
    cv2.destroyAllWindows()
  
  def Start(self):
    self.RunningThread = True
    self.__thread.start()
  
  def Stop(self):
    if self.RunningThread:
      self.RunningThread = False
      self.__thread.join()
  
  def __ProcessImage(self, img):
    # Unlikely, but we'll be safe anyways
    if img is None:
      return
    
    print("Processing image!")
    blob = cv2.dnn.blobFromImage(img, size=(300, 300), swapRB=True, crop=False)
    self.net.setInput(blob)
    vision = self.net.forward()
    
    # Draw bounding box
    cv2.rectangle(img, (self.bounds, self.bounds), (self.width-self.bounds, self.height-self.bounds), (100,0,100), 20)
    
    for output in vision[0,0,:,:]:
      classID = int(output[1])
      confidence = float(output[2])
 
      if confidence > self.mConfidence and classID == DOG:
        print(f"Found object {classID} with confidence {confidence}")
        box = output[3:7] * np.array([self.width, self.height, self.width, self.height])
        (left, top, right, bottom) = box.astype("int")
        
        cv2.rectangle(img, (left, top), (right, bottom), (100,25,0), 2)

        if left < self.bounds:
          self.commandQueue.put_nowait("left")
        elif right > self.width-self.bounds:
          self.commandQueue.put_nowait("right")
        if top < self.bounds:
          self.commandQueue.put_nowait("top")
        elif bottom >= self.height-self.bounds:
          self.commandQueue.put_nowait("bottom")
          
    if self.debugDisplay:
      print("Displaying image")
      cv2.imshow("Output", img)
    print("Image processed")
