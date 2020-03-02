# dogcam-ai
The basic AI based camera controller for the overall dogcam project. This runs and detects the dog and attempts to keep him in focus.

This is separate from the dogcam project due to the nature of how much processing power/resources this project will use because of computer vision and detection.

The end goal is to keep this running on a raspberry pi with relatively good detection rates. Currently, this detects [all of these objects](https://github.com/tensorflow/models/blob/master/research/object_detection/data/mscoco_label_map.pbtxt), but filters out any results to the given ID.

There's a few faults to this program:

* No methods of reconnection on failure or disconnection for the command server
* Better training models with small focused data sets would be of better usage. Until a better model is created, it still uses [mobilessd from tensorflow](https://github.com/opencv/opencv/wiki/TensorFlow-Object-Detection-API)
* No video stream loss detection, might be a limitation of OpenCV
* The logging is a bit much.
