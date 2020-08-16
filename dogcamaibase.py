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
  # The image to work on next
  __pendingImage = None
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
      detectionID=0):

    self.debugDisplay = displayOut
    self._bounds = int(boundsSize)
    self._minConfidence = float(minimumConfidence)
    self._image = None
    self.__pendingImage = None
    self._targetID = detectionID

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

    self.__pendingImage = image

  def __Update(self):
    # Create Debug window
    if self.debugDisplay:
      cv2.startWindowThread()
      cv2.namedWindow("Output", cv2.WINDOW_NORMAL)
      cv2.resizeWindow("Output", (320, 240))

    while self._runningThread:
      if self.__pendingImage is not None:
        self._image = self.__pendingImage
        self.__pendingImage = None
        self.__ProcessImage()
        self._image = None

        time.sleep(0.000333)

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

    ProcessingTime=time.time()
    DogCamLogger.Log(f"AI: Processing image at {ProcessingTime}!", DCLogLevel.Verbose)

    self._ProcessImageInternal()

    ProcessingTime=time.time()-ProcessingTime
    if self.debugDisplay:
      DogCamLogger.Log("AI: Displaying image", DCLogLevel.Debug)
      cv2.imshow("Output", self._image)

    DogCamLogger.Log(f"AI: Image processed in {ProcessingTime} seconds", DCLogLevel.Verbose)

  def _DrawBoundingBox(self):
    # Draw bounding box
    cv2.rectangle(self._image, (self._bounds, self._bounds), (self._width-self._bounds,
                  self._height-self._bounds), (100,0,100), 20)

  def _HandleObjectDetectionResult(self, left, right, top, bottom):
    cv2.rectangle(self._image, (left, top), (right, bottom), (100,25,0), 2)
    
    # AABB bounding collision testing
    BoxTop = (top < self._bounds)
    BoxBottom = (bottom > self._height-self._bounds)
    BoxLeft = (left <= self._bounds)
    BoxRight = (right > self._width-self._bounds)
    
    # If the dog is in a wide shot 
    # (meaning they take up the left and right collision at the same time)
    # don't attempt to over adjust
    if BoxLeft ^ BoxRight:
      if BoxLeft:
        self.commandQueue.put_nowait("left")
      else:
        self.commandQueue.put_nowait("right")
    
    # Same as the above but in portrait
    if BoxTop ^ BoxBottom:
      if BoxTop:
        self.commandQueue.put_nowait("top")
      else:
        self.commandQueue.put_nowait("bottom")
