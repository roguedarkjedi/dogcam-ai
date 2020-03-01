import numpy as np
import cv2
import time

DOG = 17
MIN_CONFIDENCE = 0.5
MIN_THRESHOLD = 0.3
print("Grabbing capture")
cap = cv2.VideoCapture("rtmp://192.168.50.4/camera/g")

if not cap.isOpened():
  print("Damn obama!")
  quit()

maxW, maxH = cap.get(cv2.CAP_PROP_FRAME_WIDTH), cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
cv2.namedWindow("Output", cv2.WINDOW_NORMAL)
cv2.resizeWindow("Output", (320, 240))
print(f"Got dimensions {maxW}x{maxH}")

# Load dnn info
net = cv2.dnn.readNetFromDarknet("./training/coco.cfg", "./training/coco.weights")
ln = net.getLayerNames()
ln = [ln[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Make a bounding box
boundingBox = (100, int(maxW - 100), 100, int(maxH - 100))
(W, H) = (None, None)

while True:
  # Pull a frame from the video
  print("Capturing")
  retVal, img = cap.read()
  if not retVal:
    print("No more data!")
    break
  
  print("Analyizing")
  if W is None or H is None:
    (H, W) = img.shape[:2]

  blob = cv2.dnn.blobFromImage(img, 1 / 255.0, (416, 416), swapRB=True, crop=False)
  net.setInput(blob)
  layerOutputs = net.forward(ln)
  boxes = []
  confidences = []
  
  print("Detecting")
  cv2.rectangle(img, (boundingBox[0], boundingBox[2]), (boundingBox[1], boundingBox[3]), (100,0,100), 20)
  # loop over each of the layer outputs
  for output in layerOutputs:
    # loop over each of the detections
    for detection in output:
      # extract the class ID and confidence (i.e., probability) of
      # the current object detection
      scores = detection[5:]
      classID = np.argmax(scores)
      confidence = scores[classID]
      
      # filter out weak predictions by ensuring the detected
      # probability is greater than the minimum probability
      #and classID == DOG
      if confidence > MIN_CONFIDENCE:
        print(f"Found object {classID}")
        box = detection[0:4] * np.array([W, H, W, H])
        (centerX, centerY, width, height) = box.astype("int")
        x = int(centerX - (width / 2))
        y = int(centerY - (height / 2))

        boxes.append([x, y, int(width), int(height)])
        confidences.append(float(confidence))
  
  print("Filtering")
  idxs = cv2.dnn.NMSBoxes(boxes, confidences, MIN_CONFIDENCE, MIN_THRESHOLD)
  
  # ensure at least one detection exists
  if len(idxs) > 0:
    # loop over the indexes we are keeping
    for i in idxs.flatten():
      # extract the bounding box coordinates
      (x, y) = (boxes[i][0], boxes[i][1])
      (w, h) = (boxes[i][2], boxes[i][3])
      
      cv2.rectangle(img, (x, y), (x+w, y+h), (100,0,0), 2)
      
      # Check Left
      if x < boundingBox[0]:
        print("Left")
      # Check Right
      elif x + w > boundingBox[1]:
        print("Right")
      # Check Bottom
      if y < boundingBox[2]:
        print("Bottom")
      # Check Top
      elif y + h >= boundingBox[3]:
        print("Top")

    
    cv2.imshow("Output", img)
    cv2.waitKey(100)

  print("Done detection")
  time.sleep(2)

cap.release()

