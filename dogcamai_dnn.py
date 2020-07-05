from dogcamlogger import DogCamLogger
from dogcamaibase import DogCamAIBase
import numpy as np
import cv2

class DogCamAIDNN(DogCamAIBase):
  # OpenCV AI network
  __net = None
  # Sync time rate with displays using OpenCV
  _fpsSyncCvTime = 1

  def __init__(self, fileLocation: str):
    self.__net = cv2.dnn.readNetFromTensorflow(fileLocation, fileLocation + "txt")
    super().__init__()

  def _ProcessImageInternal(self):
    self.__net.setInput(cv2.dnn.blobFromImage(self._image,
                size=(self._width, self._height), swapRB=True, crop=False))

    vision = self.__net.forward()

    self._DrawBoundingBox()

    # Attempt to get the objects detected in this frame
    for output in vision[0,0,:,:]:
      classID = int(output[1])
      confidence = float(output[2])

      if (self._targetID == 0 or classID == self._targetID) and confidence > self._minConfidence:
        DogCamLogger.Log(f"AI: Found object {classID} with confidence {confidence}")
        box = output[3:7] * np.array([self._width, self._height, self._width, self._height])
        (left, top, right, bottom) = box.astype("int")

        self._HandleObjectDetectionResult(left, right, top, bottom)

        # If we found the target, get out now.
        if self._targetID != 0:
          break
