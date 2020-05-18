# dogcam-ai
The basic AI based camera controller for the overall dogcam project. This runs and detects the dog and attempts to keep him in focus.

This is separate from the dogcam project due to the nature of how much processing power/resources this project will use because of computer vision and detection.

The end goal is to keep this running on a raspberry pi with relatively good detection rates. Currently, this detects [all of these objects](https://github.com/tensorflow/models/blob/master/research/object_detection/data/mscoco_label_map.pbtxt), but filters out any results to the given ID.

## Features:
---------------
* Full automation of streaming capture and frame processing
* AI detection and box overlap calculation
* All network functionality has the ability to recover from connection issues
* Lag reduction mechanics
* Safe threading design
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

If using the [Corel USB Accelerator](https://coral.ai/products/accelerator/) (Recommended), you need to also install `libedgetpu1-std python3-edgetpu` packages from the Google repro.

You can get that by following the directions found [here](https://coral.ai/docs/accelerator/get-started/#on-linux).

## Caveats:
---------------
* Better training models with small focused data sets would be of better usage. Until a better model is created, it still uses [mobilessd from tensorflow](https://github.com/opencv/opencv/wiki/TensorFlow-Object-Detection-API)
* On the Raspberry Pi 3B, a single frame with AI processing takes, on average, 2 seconds. This is the upper bounds of what this hardware can do with the given model. Using an AI accelerator is recommended.

