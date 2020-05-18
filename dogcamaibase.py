from dogcamlogger import DogCamLogger, DCLogLevel
import threading
import time
import queue
import cv2

class DogCamAIBase():
  debugDisplay = False

  # Queue of movement commands necessary for the robot.
  # The main file handles the interclass processing of these commands.
  commandQueue = queue.Queue()

  # The thread object
  _thread = None
  # The current image to display
  _image = None
  # Our thread locks for pushing in images to work with
  _lock = threading.Lock()
  # Sync time rate with displays using OpenCV
  _fpsSyncCvTime = 1
  _fpsSyncTime = 0.1
  # Width of the image to process
  _width = 0
  # Height of the image to process
  _height = 0
  # Thickness of the borders
  _bounds = 0
  # Thread flags
  _runningThread = False
  # AI Confidence levels
  _minConfidence = 0

  def __init__(self):
    DogCamLogger.Log("AI: Allocated", DCLogLevel.Verbose)

  def Initialize(self, boundsSize=100, minimumConfidence=0.3, displayOut=False,
      detectionID=0, fpsSync=0):

    self.debugDisplay = displayOut
    self._bounds = int(boundsSize)
    self._minConfidence = float(minimumConfidence)
    self._image = None
    self._targetID = int(detectionID)

    if int(fpsSync) > 0:
      self._fpsSyncTime = (1/fpsSync)
      # cv2 waitKey is in ms
      self._fpsSyncCvTime = int(self._fpsSyncTime * 1000)

    self._thread = threading.Thread(target=self.__Update)
    DogCamLogger.Log("AI: Initialized", DCLogLevel.Debug)

  def _ProcessImageInternal(self):
    raise NotImplementedError

  def SetDimensions(self, W, H):
    self._width = int(W)
    self._height = int(H)
    DogCamLogger.Log(f"AI: Resolution is {self._width}x{self._height}")

  def PushImage(self, image):
    if image is None:
      DogCamLogger.Log("AI: Image pushed was empty", DCLogLevel.Debug)
      return

    if self._lock.acquire(False) is False:
      DogCamLogger.Log("AI: Dropped frame as image is busy", DCLogLevel.Verbose)
      return

    if self._image is None:
      DogCamLogger.Log("AI: Got image to process", DCLogLevel.Debug)
      self._image = image
    else:
      DogCamLogger.Log("AI: Image pushed was dropped", DCLogLevel.Verbose)

    self._lock.release()

  def __Update(self):
    # Create Debug window
    if self.debugDisplay:
      cv2.startWindowThread()
      cv2.namedWindow("Output", cv2.WINDOW_NORMAL)
      cv2.resizeWindow("Output", (320, 240))

    while self._runningThread:
      if self._image is not None:
        self._lock.acquire()
        self.__ProcessImage()
        self._image = None
        self._lock.release()

      if self.debugDisplay:
        cv2.waitKey(self._fpsSyncCvTime)
      else:
        time.sleep(self._fpsSyncTime)

    cv2.destroyAllWindows()

  def Start(self):
    DogCamLogger.Log("AI: AI Processing Started", DCLogLevel.Notice)
    self._runningThread = True
    self._thread.start()

  def Stop(self):
    if self._runningThread:
      DogCamLogger.Log("AI: AI Processing Halted", DCLogLevel.Warn)
      self._runningThread = False
      self._thread.join()

  def __ProcessImage(self):
    # Unlikely, but we'll be safe anyways
    if self._image is None:
      DogCamLogger.Log("AI: Skipping blank image", DCLogLevel.Debug)
      return

    DogCamLogger.Log("AI: Processing image!")

    self._ProcessImageInternal()

    if self.debugDisplay:
      DogCamLogger.Log("AI: Displaying image", DCLogLevel.Debug)
      cv2.imshow("Output", self._image)

    DogCamLogger.Log("AI: Image processed")

  def _DrawBoundingBox(self):
    # Draw bounding box
    cv2.rectangle(self._image, (self._bounds, self._bounds), (self._width-self._bounds,
                  self._height-self._bounds), (100,0,100), 20)

  def _HandleObjectDetectionResult(self, left, right, top, bottom):
    cv2.rectangle(self._image, (left, top), (right, bottom), (100,25,0), 2)

    if left < self._bounds:
      self.commandQueue.put_nowait("left")
    elif right > self._width-self._bounds:
      self.commandQueue.put_nowait("right")
    if top < self._bounds:
      self.commandQueue.put_nowait("top")
    elif bottom >= self._height-self._bounds:
      self.commandQueue.put_nowait("bottom")
