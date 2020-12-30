# dogcam-ai
The basic AI based camera controller for the overall dogcam project which aims to detects the animal and keep them in focus.

This is separate from the base project due to the nature of how much processing power/resources this program requires due to the usage of computer vision, video processing and object detection.

The end goal is to keep this running on a raspberry pi with relatively good detection rates. Currently, this detects [all of these objects](https://github.com/tensorflow/models/blob/master/research/object_detection/data/mscoco_label_map.pbtxt), but can filter out results to a given ID.

## Features:
---------------
* Full automation of streaming capture and frame processing
* AI detection and box overlap calculation
* All network functionality has the ability to recover from connection issues
* Lag reduction mechanics
* Mostly configurable
* Logging spew control
* Support for USB accelerators
* Extensible for additional hardware ai devices

## Install:
---------------
1. Grab the OpenCV libraries [from here](https://github.com/dlime/Faster_OpenCV_4_Raspberry_Pi)
2. Install all the required modules `python3 -m pip install --upgrade -r requirements.txt`
3. Change values in the config.json
4. Run main.py

If using the [Corel USB Accelerator](https://coral.ai/products/accelerator/) (Recommended), you need to also install `libedgetpu1-std python3-edgetpu` packages from the Google repro. You can get that by following the directions found [on this website](https://coral.ai/docs/accelerator/get-started/#on-linux).

## Configuration:
-----------------

### Streaming
**StreamingURL**: is the rtmp ingest url for the webcam.  
**StreamingCaptureRate**: the delay between capturing an frame to propose it for AI processing (if we haven't grabbed a newer frame).  
**StreamingFrameBufferSize**: How big of a frame buffer the streaming capture has. Lower is less resource usage.  
**StreamingTimeout**: The amount of time from no longer getting a new frame that we consider the rtmp server to be disconnected.  

### Servo Control
**CommandsAddress**: The websocket server location that's running [dogcam](https://github.com/roguedarkjedi/dogcam).  
**CommandsTimeout**: The amount of time in seconds from the last message/keepalive to consider the server to be disconnected.  

### AI
**AIMethod**: Current valid values are `"dnn"` and `"tf"`. If set to `tf`, the USB Accelerator libraries are used. Otherwise, OpenCV's dnn method will be used to process the images from the camera.  
**AIModels**: A json dictionary that contains the relative paths to the AI model files. Valid keys are `"dnn"` and `"tf"`. Your current `AIMethod` must have a defined model or the program will crash.  
**AIDisplayVision**: Have the AI display on screen what it sees as it runs. This does run slightly slower.  
**AIBoundsSize**: The bounding box around the edges of the screen. This dictates how far away from the screen boundaries to place the edge detection. If an object overlaps or intersects this will cause commands to be sent to the websocket server.  
**AIMinimumConfidence**: The minimum confidence level to consider the an object for detection.  
**AIDetectID**: The label id for the class detection to filter on ([ids found here](https://github.com/tensorflow/models/blob/master/research/object_detection/data/mscoco_label_map.pbtxt)). If set to 0, all detected objects can cause commands to be sent. It is recommended you fill this config with a number other than 0. If you would like to detect more than one object, this config does take a json array with the ids that will also generate positives (the first object detected will be acted upon).  

### Misc
**LoggingLevel**: The logging spew level for the output console. Any messages with values higher than the setting will be suppressed. Passing `silence` will mute all messages.  

A list of valid options can be seen below:  
```
  Debug
  Verbose
  Log
  Warn
  Error
  Notice
  Silence
```

## Caveats:
---------------
* Better training models with small focused data sets would be of better usage. Until a better model is created, this project still uses [mobilessd from tensorflow](https://github.com/opencv/opencv/wiki/TensorFlow-Object-Detection-API). For the usb accelerated functionality, [this model is used](https://dl.google.com/coral/canned_models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite).
* On the Raspberry Pi 3B, a single frame with AI processing takes on average, 2 seconds. This is the upper bounds of what this hardware can do with the given model. Using an AI accelerator is recommended.
* On a Raspberry Pi 3B, this program does incredibly well with an ingest of 720p/24fps @ 2500kbps. Anything higher has been observed to induce video decoding latency on the box.
