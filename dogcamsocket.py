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
      print("Websocket: Socket constructing")

    try:
      self.__socket = websocket.WebSocket()
      self.__socket.connect(self.URL)
      print("Websocket: Socket connected!")
      self.__OnConnected()
    except KeyboardInterrupt:
      print("Websocket: Interrupted!")
      raise
    except Exception as ex:
      print(f"Websocket: Failed to connect!\nException: {ex}")
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
    if self.__processing is False or self.__socket is None or self.__reconnect is True:
      print("Websocket: Not connected!")
      return

    JsonMessage = {
      "action": direction,
      "source": "dogcamai"
    }

    print("Websocket: Sending new postion message")
    self.__socket.send(json.dumps(JsonMessage))

  def __OnConnected(self):
    self.__processing = True
    self.__reconnectTimeout = 0.0
    if self.__thread is None:
      self.__thread = threading.Thread(target=self.__MessageThread, daemon=True, name="WSThread")
      self.__thread.start()

  def __MessageThread(self):
    while self.__processing:

      # Attempt to handle reconnection
      if self.__socket is None:

        # Handle timeouts
        if self.__reconnectTimeout == 0.0:
          print("Websocket: Detected disconnection")
          self.__reconnectTimeout = time.time()
          self.__reconnect = True
        elif (time.time() - self.__reconnectTimeout) >= self.__maxTimeout:
          print("Websocket: Exhausted retries to reconnect")
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

        print(f"Websocket: Got message: {Message}")

      except websocket.WebSocketConnectionClosedException:
        print("Websocket: was disconnected!")
        self.__socket = None
        continue
      except KeyboardInterrupt:
        break

      time.sleep(0.5)
