from dogcamlogger import DogCamLogger
from dogcamaibase import DogCamAIBase
from edgetpu.detection.engine import DetectionEngine
from PIL import Image
import cv2

class DogCamAITFLite(DogCamAIBase):
  __net = None

  def __init__(self, fileLocation:str):
    self.__net = DetectionEngine(fileLocation)
    super().__init__()

  def _ProcessImageInternal(self):
    self._image = cv2.resize(self._image, (self._width, self._height))

    img = self._image.copy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)

    # Run the tensorflow model
    detectionData = self.__net.detect_with_image(img, self._minConfidence, top_k=5,
      keep_aspect_ratio=True, relative_coord=False)

    for obj in detectionData:
      if (self._targetID == 0 or obj.label_id == self._targetID):
        DogCamLogger.Log(f"AI: Found object {obj.label_id} with confidence {obj.score}")

        # Get the bounding box of the object
        box = obj.bounding_box.flatten().astype(int)
        (left, top, right, bottom) = box

        self._HandleObjectDetectionResult(left, right, top, bottom)

        # If we found the target, get out now.
        if self._targetID != 0:
          break
