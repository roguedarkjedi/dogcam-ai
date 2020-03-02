import cv2
import numpy as np
import threading
import time
import queue

# https://github.com/pjreddie/darknet/blob/master/data/coco.names
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
  debugDisplay = False
  
  commandQueue = queue.Queue()
  
  __thread = None
  __image = None
  __lock = threading.Lock()
  
  def __init__(self, boundsSize=100, minimumConfidence=0.25, minimumThreshold=0.3):
    self.net = cv2.dnn.readNetFromDarknet("./training/coco-tiny.cfg", "./training/coco-tiny.weights")
    self.ln = self.net.getLayerNames()
    self.ln = [self.ln[i[0] - 1] for i in self.net.getUnconnectedOutLayers()]
    self.bounds = boundsSize
    self.mConfidence = minimumConfidence
    self.mThreshold = minimumThreshold
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
      if self.debugDisplay:
        cv2.imshow("Output", img)
      
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
        
        cv2.rectangle(img, (x, y), (x+w, y+h), (100,25,0), 2)

        if x < self.bounds:
          self.commandQueue.put_nowait("left")
        elif x + w > self.width-self.bounds:
          self.commandQueue.put_nowait("right")
        if y < self.bounds:
          self.commandQueue.put_nowait("top")
        elif y + h >= self.height-self.bounds:
          self.commandQueue.put_nowait("bottom")
          
    if self.debugDisplay:
      print("Displaying image")
      cv2.imshow("Output", img)
    print("Image processed")
