import cv2
import numpy as np
import threading
import time
import queue

DOG = 17

class DogCamAI():
  net = None
  ln = None
  width = 0
  height = 0
  bounds = 0
  mConfidence = 0
  mThreshold = 0
  RunningThread = False
  debugDisplay = True
  
  commandQueue = queue.Queue()
  
  __thread = None
  __image = None
  __lock = threading.Lock()
  
  def __init__(self, boundsSize=100, minimumConfidence=0.5, minimumThreshold=0.3):
    self.net = cv2.dnn.readNetFromDarknet("./training/coco.cfg", "./training/coco.weights")
    self.ln = self.net.getLayerNames()
    self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
    self.bounds = boundsSize
    self.mConfidence = minimumConfidence
    self.mThreshold = minimumThreshold
    self.__image = None
    
    
    # Create Debug window
    cv2.namedWindow("Output", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Output", (320, 240))
    
    self.__thread = threading.Thread(target=self.__Update)
    
  def SetDimensions(self, W, H):
    self.width = int(W)
    self.height = int(H)
    
  def PushImage(self, image):
    if self.__lock.acquire(False) is False:
      return
    
    if self.__image is None and image is not None:
      print("Got image to process")
      self.__image = image
    self.__lock.release()
  
  def __Update(self):
    while self.RunningThread:
      if self.__image is not None:
        self.__lock.acquire()
        self.__ProcessImage(self.__image)
        self.__image = None
        self.__lock.release()
      
      time.sleep(1)
  
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
    blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False)
    self.net.setInput(blob)
    layerOutputs = self.net.forward(self.ln)
    boxes = []
    confidences = []
    
    # Draw bounding box
    cv2.rectangle(img, (self.bounds, self.bounds), (self.width-self.bounds, self.height-self.bounds), (100,0,100), 20)
    
    for output in layerOutputs:
      for detection in output:
        # pull data regarding the detection
        scores = detection[5:]
        classID = np.argmax(scores)
        confidence = scores[classID]

        # filter out weak predictions by ensuring the detected
        # probability is greater than the minimum probability
        #and classID == DOG
        if confidence > self.mConfidence:
          print(f"Found object {classID} with confidence {confidence}")
          box = detection[0:4] * np.array([self.width, self.height, self.width, self.height])
          (centerX, centerY, width, height) = box.astype("int")
          x = int(centerX - (width / 2))
          y = int(centerY - (height / 2))

          boxes.append([x, y, int(width), int(height)])
          confidences.append(float(confidence))
    
    if len(confidences) == 0:
      print("Found nothing, exiting!")
      return

    # Attempt to clean up detection
    print("Cleaning up detection")
    idxs = cv2.dnn.NMSBoxes(boxes, confidences, self.mConfidence, self.mThreshold)
    
    if len(idxs) > 0:
      # loop over the indexes we are keeping
      for i in idxs.flatten():
        # Get BB coordinates
        (x, y) = (boxes[i][0], boxes[i][1])
        (w, h) = (boxes[i][2], boxes[i][3])
        
        cv2.rectangle(img, (x, y), (x+w, y+h), (100,0,0), 2)

        # Check Left
        if x < self.bounds:
          self.commandQueue.put_nowait("left")
        # Check Right
        elif x + w > self.width-self.bounds:
          self.commandQueue.put_nowait("right")
        # Check Bottom
        if y < self.bounds:
          self.commandQueue.put_nowait("bottom")
        # Check Top
        elif y + h >= self.height-self.bounds:
          self.commandQueue.put_nowait("top")
          
    if self.debugDisplay:
      print("Displaying image")
      cv2.imshow("Output", img)
    print("Image processed")
