from dogcamlogger import DogCamLogger
from dogcamaibase import DogCamAIBase
from pycoral.adapters import common, detect
from pycoral.utils.edgetpu import make_interpreter
from PIL import Image
import cv2

class DogCamAITFLite(DogCamAIBase):
  __net = None

  def __init__(self, fileLocation:str):
    self.__net = make_interpreter(fileLocation)
    self.__net.allocate_tensors()
    super().__init__()

  def _ProcessImageInternal(self):
    img = self._image.copy()
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)

    # Prepare image data
    _, scale = common.set_resized_input(self.__net, img.size, lambda size : img.resize(size, Image.ANTIALIAS))

    # Invoke the model
    self.__net.invoke()

    # Run the tensorflow model
    detectionData = detect.get_objects(self.__net, self._minConfidence, scale)

    for obj in detectionData:
      if (not self._targetID or (isinstance(self._targetID, list) and obj.id in self._targetID)):
        self._LogObjectFound(obj.id, obj.score)

        # Get the bounding box of the object
        box = obj.bbox

        self._HandleObjectDetectionResult(box.xmin, box.xmax, box.ymin, box.ymax)

        # If we found atleast one object, then we can exit out.
        break

    self._DrawBoundingBox()
