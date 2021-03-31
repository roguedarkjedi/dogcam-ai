# dogcam-ai
The basic AI based camera controller for the overall dogcam project which aims to detects the animal and keep them in focus.

This is separate from the base project due to the nature of how much processing power/resources this program requires due to the usage of computer vision, video processing and object detection.

The end goal is to keep this running on a raspberry pi with relatively good detection rates. Currently, this detects [all of these objects](https://github.com/tensorflow/models/blob/master/research/object_detection/data/mscoco_label_map.pbtxt), but can filter out results to a given ID.

## Features:
* Full automation of streaming capture and frame processing
* AI detection and box overlap calculation
* All network functionality has the ability to recover from connection issues
* Lag reduction mechanics
* Mostly configurable
* Logging spew control
* Support for USB accelerators
* Extensible for additional hardware ai devices

## Install:
1. Grab the OpenCV libraries [from here](https://github.com/dlime/Faster_OpenCV_4_Raspberry_Pi)
2. Install all the required modules `python3 -m pip install --upgrade -r requirements.txt`
3. [Download a model](#models) that fits your current needs.
4. Change values in the config.json to [fit your configuration](#configuration)
5. Execute Run.sh

If using the [Coral USB Accelerator](https://coral.ai/products/accelerator/) (Recommended), you need to also install additional packages for using the Coral accelerator. You can get them by following the directions found [on this website](https://coral.ai/docs/accelerator/get-started/#on-linux).

## Models:
Better training models with small focused data sets would be of better usage. 

Regardless, this project uses [mobilessd from tensorflow](https://github.com/opencv/opencv/wiki/TensorFlow-Object-Detection-API) for dnn processing. 

If using the usb accelerated functionality, [this model is used](https://dl.google.com/coral/canned_models/mobilenet_ssd_v2_coco_quant_postprocess_edgetpu.tflite) instead.

## Configuration:

### Streaming
**StreamingURL**: is the rtmp ingest/device uri for the webcam.  
**StreamingFrameBufferSize**: How big of a frame buffer the streaming capture has. Lower is less resource usage.  
**StreamingTimeout**: The amount of time from no longer getting a new frame that we consider the rtmp server to be disconnected. Sockets typically timeout within 30 seconds, so it's advised to keep this value at 120 or greater to allow for retries.  

### Servo Control
**CommandsAddress**: The websocket server location that's running [dogcam](https://github.com/roguedarkjedi/dogcam).  
**CommandsTimeout**: The amount of time in seconds from the last message/keepalive to consider the server to be disconnected.  

### AI
**AIMethod**: Current valid values are `"dnn"` and `"tf"`. If set to `tf`, the USB Accelerator libraries are used. Otherwise, OpenCV's dnn method will be used to process the images from the camera.  
**AIModels**: A json dictionary that contains the relative paths to the AI model files. Valid keys are `"dnn"` and `"tf"`. Your current `AIMethod` must have a defined model or the program will crash.  
**AIDisplayVision**: Have the AI display on screen what it sees as it runs. This does run slightly slower.  
**AIBoundsXSize**: The bounding box length around the edges of the screen. This dictates how far away from the screen boundaries to place the edge detection. If an object overlaps or intersects this will cause commands to be sent to the websocket server.  
**AIBoundsYSize**: Same as above but for height.  
**AIMinimumConfidence**: The minimum confidence level to consider the an object for detection.  
**AIDetectID**: The label id for the class detection to filter on ([ids found here](https://github.com/tensorflow/models/blob/master/research/object_detection/data/mscoco_label_map.pbtxt)). If set to 0, all detected objects can cause commands to be sent. It is recommended you fill this config with a number other than 0. If you would like to detect more than one object, this config does take a json array with the ids that will also generate positives (the first object detected will be acted upon).  
**AILogMatches**: Controls the log messaging spew if the AI should print out every time it detects an object. Processing is better with this set to false.  
**AIThrottleTilt**: This attempts to throttle tilt commands during motion. I've found sometimes the AI sends back a bounding box that's just a little too tall during motion, and that can throw off the detection. However, this could have been a red-herring caused by some delays while processing the video feed. Regardless, this setting is here to limit the number of tilt commands within a certain interval.  
**AITiltCooldown**: The interval to block tilt commands. If a tilt command is generated within this amount of time since the last tilt command, it will be dropped (unsent). This only has an affect if `AIThrottleTilt` is set to true.  

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

## Performance:
Performance metrics were gathered using input video from the [Streamlabs mobile app](https://streamlabs.com/mobile-app) on an iPhone 6s using 720p/24fps @ 2500kbps with low Audio quality settings.  

Alternative apps that are free based have been tested and sadly have been found that they perform worse on average. It is unknown what Streamlabs does in their video pipeline to make it so efficient, and it is likely they will not relay that information to anyone.  

It is heavily recommended to use an AI accelerator chip to offload a lot of the work burden of the AI detection. Performance metrics were a [massive improvement early on in the project and continued to be to the end](https://github.com/roguedarkjedi/dogcam-ai/issues/15).

### Raspberry Pi 3B
---------------------
This is based off a Raspberry Pi 3B 1GB model  

* Without an accelerator, a single frame of AI processing takes on average, two seconds. This is the upper bounds of what this hardware can do with the given model.  
* With an accelerator, on average, about eight frames of AI processing can be done within a second. These calculations were on an earlier revision of the software so they are out of date.  

Due to the amount of work that goes on in this program, it is recommended to exclusively use the Pi host for just this project and/or dogcam. Anything more will push the hardware past its limitations. It's theorized that this is mostly due to the sheer amount of bandwidth of data in flight through the chip and power draw for a 3B.  

### Raspberry Pi 4B
---------------------
This is based off a Raspberry Pi 4B 4GB model  

This is the golden path for this project. Running the software on here with an acelerator allows for the Pi to be able to multitask extremely well. This leads to near real-time processing and action with such minimal latency that it is unnoticable.  

Because the Pi 4B has several improvements to the hardware model (namely a separated network interface chip and USB 3.0 support, allowing for better bandwidth and cross direction data), this is the recommended hardware to run the AI model on. However, the CAD files for the dogcam project was designed for a 3B, so modifications would have to be made to have a fully moble device.  

## Final Notes:
* Using an AI accelerator chip is extremely recommended as it lowers object detection and processing time to a level where its production ready for a stream. You may be able to run this system without an accelerator on a Pi 4B just fine.
* If using an accelerator chip, cooling must be fully considered and implemented to avoid damage to any parts.
* Moving forward the old capture limiter has been removed, resources can no longer be committed to making sure that it's even useful for lower spec machines (e.g. without AI accelerator chips), but if needed, it can be [found here](https://github.com/roguedarkjedi/dogcam-ai/tree/noaccel).

