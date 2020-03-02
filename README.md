# dogcam-ai
The AI based camera controller for the dogcam project. This runs and detects the dog and attempts to keep him in focus. This is separate from the dogcam project due to the nature of how much processing power/resources this project will use due to the nature of it (to make it easier to taskkill haha).

The end goal is to keep this running on a raspberry pi with relatively good detection rates.

There's a few faults to this program:

* No methods of reconnection on failure or disconnection (there is a video feed staller, but the websocket does not believe in reconnecting)
* Better training models with small focused data sets would be of better usage. Until a better model is created, it still uses [mobilessd from tensorflow](https://github.com/opencv/opencv/wiki/TensorFlow-Object-Detection-API)
* No video stream loss detection, might be a limitation of OpenCV
