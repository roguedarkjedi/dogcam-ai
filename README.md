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

## Install:
---------------
1. Grab the OpenCV libraries [from here](https://github.com/dlime/Faster_OpenCV_4_Raspberry_Pi)
2. Install all the required modules `python3 -m pip install --upgrade -r requirements.txt`
3. Change values in the config.json
4. Run main.py

## Caveats:
---------------
* Better training models with small focused data sets would be of better usage. Until a better model is created, it still uses [mobilessd from tensorflow](https://github.com/opencv/opencv/wiki/TensorFlow-Object-Detection-API)
* OpenCV install process needs to be specifically targeted for the Raspberry Pi otherwise process times take about 2s per frame, which is intense.
* Image processing on a Raspberry Pi using the dnn module takes 2s per frame. There might be faster methods.
