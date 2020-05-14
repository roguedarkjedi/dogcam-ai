import cv2
import numpy as np
import threading
import time
import queue

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
  __fpsSyncTime = 1
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
      self.__fpsSyncTime = ((1/fpsSync) * 1000)

    self.__thread = threading.Thread(target=self.__Update)
    print("AI: Initialized")

  def SetDimensions(self, W, H):
    self.__width = int(W)
    self.__height = int(H)
    print(f"AI: Resolution is {self.__width}x{self.__height}")

  def PushImage(self, image):
    if self.__lock.acquire(False) is False:
      return

    if self.__image is None and image is not None:
      print("AI: Got image to process")
      self.__image = image
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
        self.__ProcessImage(self.__image)
        self.__image = None
        self.__lock.release()

      if self.debugDisplay:
        cv2.waitKey(self.__fpsSyncTime)

      time.sleep(0.2)
    cv2.destroyAllWindows()

  def Start(self):
    self.__runningThread = True
    self.__thread.start()

  def Stop(self):
    if self.__runningThread:
      self.__runningThread = False
      self.__thread.join()

  def __ProcessImage(self, img):
    # Unlikely, but we'll be safe anyways
    if img is None:
      return

    print("AI: Processing image!")
    blob = cv2.dnn.blobFromImage(img, size=(300, 300), swapRB=True, crop=False)
    self.__net.setInput(blob)
    vision = self.__net.forward()

    # Draw bounding box
    cv2.rectangle(img, (self.__bounds, self.__bounds), (self.__width-self.__bounds, self.__height-self.__bounds), (100,0,100), 20)

    for output in vision[0,0,:,:]:
      classID = int(output[1])
      confidence = float(output[2])

      if confidence > self.__minConfidence and (self.__targetID == 0 or classID == self.__targetID):
        print(f"AI: Found object {classID} with confidence {confidence}")
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

    if self.debugDisplay:
      print("AI: Displaying image")
      cv2.imshow("Output", img)
    print("AI: Image processed")
