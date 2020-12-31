from dogcamlogger import DogCamLogger, DCLogLevel
import websocket
import threading
import time
import json

class DogCamSocket():
  __socket = None
  __thread = None
  __processing = False
  __reconnect = False
  __reconnectTimeout = 0.0
  __maxTimeout = 0.0
  URL = ""

  def __init__(self, dest, MaxTimeout=120.0):
    self.__maxTimeout = float(MaxTimeout)
    self.URL = dest

  def Connect(self):
    self.__reconnect = False
    try:
      self.__socket.close()
      self.__socket = None
    except:
      DogCamLogger.Log("Websocket: Socket constructing")

    try:
      self.__socket = websocket.WebSocket()
      self.__socket.connect(self.URL)
      DogCamLogger.Log("Websocket: Socket connected!", DCLogLevel.Notice)
      self.__OnConnected()
    except KeyboardInterrupt:
      DogCamLogger.Log("Websocket: Interrupted!", DCLogLevel.Debug)
      raise
    except Exception as ex:
      DogCamLogger.Log(f"Websocket: Failed to connect!\nException: {ex}", DCLogLevel.Warn)
      self.__socket = None
      self.__reconnect = True

  def Disconnect(self):
    self.__processing = False
    self.__reconnect = False

    if self.__socket is not None:
      self.__socket.close()
      self.__socket = None

    if self.__thread is not None:
      self.__thread.join()

  def SendPosition(self, direction):
    JsonMessage = {
      "action": direction,
      "type": "action",
      "source": "dogcamai"
    }

    self.SendMessage(json.dumps(JsonMessage))

  def IsConnectionReady(self):
    return not (self.__processing is False or self.__socket is None or self.__reconnect is True)

  # This function should typically be given json but does not check to see if you have given it valid json
  # as it doesn't essentially require json
  def SendMessage(self, message):
    if self.IsConnectionReady() is False:
      return
    
    if message is None:
      return

    self.__socket.send(message)

  def __OnConnected(self):
    self.__processing = True
    self.__reconnectTimeout = 0.0
    if self.__thread is None:
      self.__thread = threading.Thread(target=self.__MessageThread, daemon=True, name="WSThread")
      self.__thread.start()

  def __MessageThread(self):
    while self.__processing:

      # Attempt to handle reconnection
      if self.IsConnectionReady() is False:

        # Handle timeouts
        if self.__reconnectTimeout == 0.0:
          DogCamLogger.Log("Websocket: Detected disconnection", DCLogLevel.Warn)
          self.__reconnectTimeout = time.time()
          self.__reconnect = True
        elif (time.time() - self.__reconnectTimeout) >= self.__maxTimeout:
          DogCamLogger.Log("Websocket: Exhausted retries to reconnect", DCLogLevel.Error)
          self.__processing = False
          break

        if self.__reconnect is True:
          self.Connect()

        time.sleep(2)
        continue

      try:
        Message = self.__socket.recv()
        if not Message:
          time.sleep(1)
          continue

        DogCamLogger.Log(f"Websocket: Got message: {Message}", DCLogLevel.Debug)

      except (websocket.WebSocketConnectionClosedException, BrokenPipeError):
        DogCamLogger.Log("Websocket: was disconnected!", DCLogLevel.Warn)
        self.__socket = None
        continue
      except KeyboardInterrupt:
        break

      time.sleep(0.5)
