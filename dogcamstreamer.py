from dogcamlogger import DogCamLogger, DCLogLevel
import cv2
import threading
import time

class DogCamStreamer():
  __cap = None
  __img = None
  __thread = None

  __Running = False
  __LastReadTime = 0.0
  __LastErrorTime = 0.0
  __LastConnectionAttempt = 0.0
  __HasBeenFlushed = False

  resWidth = 0
  resHeight = 0
  fbSize = 0
  fpsRate = 0.0
  vidURL = ""
  captureRate=0.0
  netTimeout=0.0

  def __init__(self, inURL, timeBetweenCaptures=5.0, disconnectionTimeout=10.0, frameBufferSize=5):
    self.vidURL = inURL

    self.captureRate = timeBetweenCaptures
    self.netTimeout = disconnectionTimeout
    self.fbSize = frameBufferSize

  def Open(self):
    DogCamLogger.Log("Webstream: Loading video feed", DCLogLevel.Notice)
    if self.__cap is not None:
      DogCamLogger.Log("Webstream: Another capture instance already exists", DCLogLevel.Warn)
    
    self.__LastConnectionAttempt = time.time()
    self.__cap = cv2.VideoCapture(self.vidURL)
    self.__HasBeenFlushed = False

    # Keep only a few frames in the buffer, dropping dead frames
    self.__cap.set(cv2.CAP_PROP_BUFFERSIZE, self.fbSize)

    if not self.__cap.isOpened():
      DogCamLogger.Log("Webstream: Could not capture the video!", DCLogLevel.Warn)
      self.__cap = None
      return False

    if self.resWidth == 0:
      self.resWidth = self.__cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    if self.resHeight == 0:
      self.resHeight = self.__cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    
    self.__LastErrorTime = 0.0
    return True

  # Called by outside functions to get us going
  def Start(self):
    # if we already have a running instance, don't start it again
    if self.__cap is not None:
      return True
    
    if self.Open():
      DogCamLogger.Log("Webstream: Starting thread")
      self.__Running = True
      self.__thread = threading.Thread(target=self.__Update, daemon=True)
      self.__thread.start()
      return True
    else:
      DogCamLogger.Log("Webstream: Failed to start!", DCLogLevel.Warn)
      self.Stop()

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
    timeSinceError = (time.time() - self.__LastErrorTime)
    lastConnectionAttempt = (time.time() - self.__LastConnectionAttempt)
    
    isTotalDisconnection = timeSinceError >= self.netTimeout and self.__LastErrorTime > 0.0
    isConnectionRetry = (self.__cap is None or self.__cap.isOpened() is False) and lastConnectionAttempt >= 5.0

    # See if we should check to restart the capture software again
    if isTotalDisconnection:
      # At this point we are starved of updates entirely and we fail out.
      DogCamLogger.Log("Webstream: Timeout has occurred!", DCLogLevel.Notice)
      self.__Running = False
      self.__ReleaseCapture()
      self.__BlankImage()
      return False
    elif isConnectionRetry:
      DogCamLogger.Log("Webstream: Attempting to restart capture", DCLogLevel.Log)
      self.__BlankImage()
      self.__ReleaseCapture()
      self.Open()
      time.sleep(1)

    return True

  def __SetError(self):
    # If we already have a pending error time, then we're already handling this issue somewhere else
    if self.__LastErrorTime <= 1.0:
      DogCamLogger.Log("Webstream: Detected error, waiting...", DCLogLevel.Error)
      self.__LastErrorTime = time.time()
      self.__BlankImage()
      self.__ReleaseCapture()

  def __BlankImage(self):
    DogCamLogger.Log("Webstream: Blanking image", DCLogLevel.Debug)
    self.__img = None

  # Easy function to just sleep appropriately
  def __FPSSync(self):
    time.sleep(0.00033)

  def __Update(self):
    while self.__Running:
      # If we lose our device, stop this thread.
      if self.__CheckTimeout() is False:
        break

      # if we suddenly lose our instance, set an error flag and attempt to get it again
      if self.__cap is None:
        self.__SetError()
        self.__FPSSync()
        continue

      retVal, image  = self.__cap.read()

      if not retVal:
        self.__SetError()
        self.__FPSSync()
        continue
      # TODO: Heavily consider dropping the capture rate functionality here. While it's rather silly, it's to attempt
      # to limit the number of resize operations that are done on the image, saving some CPU cycles.
      elif not self.__HasBeenFlushed or ((time.time() - self.__LastReadTime) >= self.captureRate and self.__HasBeenFlushed):
        DogCamLogger.Log("Webstream: Capturing image", DCLogLevel.Verbose)
        self.__img = cv2.resize(image, (self.resWidth, self.resHeight))
        self.__LastReadTime = time.time()
        self.__HasBeenFlushed = False
        if self.__LastErrorTime > 0.0:
          DogCamLogger.Log("Webstream: Recovered from net disruption")
          self.__LastErrorTime = 0
      else:
        DogCamLogger.Log("Webstream: Dropped frame (safe)", DCLogLevel.Verbose)
        # Since the frame is going to be dropped, clear the frame buffer to prevent acting on old data
        self.__BlankImage()

      self.__FPSSync()

  def Read(self):
    # Pulls the current image from the framebuffer var
    retImg = self.__img
    self.__HasBeenFlushed = True
    #print(f"it has been {(time.time() - self.__LastReadTime)} seconds since grab")
    return retImg

  # If the thread is currently running
  def Running(self):
    return self.__Running
  
  # This resets the current instance, opting to force a reconnection.
  def Reset(self):
    self.__SetError()
    self.__FPSSync()

  # Stops this instance
  def Stop(self):
    self.__Running = False
    self.__BlankImage()

    if self.__thread is not None:
      self.__thread.join()

    self.__ReleaseCapture()
