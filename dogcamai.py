from dogcamlogger import DogCamLogger, DCLogLevel
import numpy as np
import threading
import time
import queue
import cv2

class DogCamAI():
  debugDisplay = False

  # Queue of movement commands necessary for the robot.
  # The main file handles the interclass processing of these commands.
  commandQueue = queue.Queue()

  # OpenCV AI network
  __net = None
  # The thread object
  __thread = None
  # The current image to display
  __image = None
  # Our thread locks for pushing in images to work with
  __lock = threading.Lock()
  # Sync time rate with displays using OpenCV
  __fpsSyncCvTime = 1
  __fpsSyncTime = 0.1
  # Width of the image to process
  __width = 0
  # Height of the image to process
  __height = 0
  # Thickness of the borders
  __bounds = 0
  # Thread flags
  __runningThread = False
  # AI Confidence levels
  __minConfidence = 0

  def __init__(self, boundsSize=100, minimumConfidence=0.3, displayOut=False, detectionID=0, fpsSync=0):
    self.__net = cv2.dnn.readNetFromTensorflow("./training/mobilenet.pb", "./training/mobilenet.pbtxt")
    self.debugDisplay = displayOut
    self.__bounds = int(boundsSize)
    self.__minConfidence = float(minimumConfidence)
    self.__image = None
    self.__targetID = int(detectionID)

    if int(fpsSync) > 0:
      # cv2 waitKey is in ms
      self.__fpsSyncTime = (1/fpsSync)
      self.__fpsSyncCvTime = int(self.__fpsSyncTime * 1000)

    self.__thread = threading.Thread(target=self.__Update)
    DogCamLogger.Log("AI: Initialized", DCLogLevel.Debug)

  def SetDimensions(self, W, H):
    self.__width = int(W)
    self.__height = int(H)
    DogCamLogger.Log(f"AI: Resolution is {self.__width}x{self.__height}")

  def PushImage(self, image):
    if image is None:
      DogCamLogger.Log("AI: Image pushed was empty", DCLogLevel.Debug)
      return

    if self.__lock.acquire(False) is False:
      DogCamLogger.Log("AI: Dropped frame as image is busy", DCLogLevel.Verbose)
      return

    if self.__image is None:
      DogCamLogger.Log("AI: Got image to process", DCLogLevel.Debug)
      self.__image = image
    else:
      DogCamLogger.Log("AI: Image pushed was dropped", DCLogLevel.Verbose)

    self.__lock.release()

  def __Update(self):
    # Create Debug window
    if self.debugDisplay:
      cv2.startWindowThread()
      cv2.namedWindow("Output", cv2.WINDOW_NORMAL)
      cv2.resizeWindow("Output", (320, 240))

    while self.__runningThread:
      if self.__image is not None:
        self.__lock.acquire()
        self.__ProcessImage()
        self.__image = None
        self.__lock.release()

      if self.debugDisplay:
        cv2.waitKey(self.__fpsSyncCvTime)
      else:
        time.sleep(self.__fpsSyncTime)

    cv2.destroyAllWindows()

  def Start(self):
    DogCamLogger.Log("AI: AI Processing Started", DCLogLevel.Notice)
    self.__runningThread = True
    self.__thread.start()

  def Stop(self):
    if self.__runningThread:
      DogCamLogger.Log("AI: AI Processing Halted", DCLogLevel.Warn)
      self.__runningThread = False
      self.__thread.join()

  def __ProcessImage(self):
    # Unlikely, but we'll be safe anyways
    if self.__image is None:
      DogCamLogger.Log("AI: Skipping blank image", DCLogLevel.Debug)
      return

    DogCamLogger.Log("AI: Processing image!")
    blob = cv2.dnn.blobFromImage(self.__image, size=(300, 300), swapRB=True, crop=False)
    self.__net.setInput(blob)
    vision = self.__net.forward()

    # Draw bounding box
    cv2.rectangle(self.__image, (self.__bounds, self.__bounds), (self.__width-self.__bounds, self.__height-self.__bounds), (100,0,100), 20)

    # Attempt to get the objects detected in this frame
    for output in vision[0,0,:,:]:
      classID = int(output[1])
      confidence = float(output[2])

      if (self.__targetID == 0 or classID == self.__targetID) and confidence > self.__minConfidence:
        DogCamLogger.Log(f"AI: Found object {classID} with confidence {confidence}")
        box = output[3:7] * np.array([self.__width, self.__height, self.__width, self.__height])
        (left, top, right, bottom) = box.astype("int")

        cv2.rectangle(img, (left, top), (right, bottom), (100,25,0), 2)

        if left < self.__bounds:
          self.commandQueue.put_nowait("left")
        elif right > self.__width-self.__bounds:
          self.commandQueue.put_nowait("right")
        if top < self.__bounds:
          self.commandQueue.put_nowait("top")
        elif bottom >= self.__height-self.__bounds:
          self.commandQueue.put_nowait("bottom")

        # If we found the target, get out now.
        if self.__targetID != 0:
          break

    if self.debugDisplay:
      DogCamLogger.Log("AI: Displaying image", DCLogLevel.Debug)
      cv2.imshow("Output", self.__image)
    DogCamLogger.Log("AI: Image processed")
