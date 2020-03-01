import websocket
import threading
import time
import json

class DogCamSocket():
  __socket: None
  __thread: None
  URL: ""
  Processing: False
  
  def __init__(self, dest):
    self.URL = dest
    self.__socket = websocket.WebSocket()
    
  def __del__(self):
    self.Disconnect()
    
  def Connect(self):
    try:
      self.__socket.connect(self.URL)
      print("Socket connected!")
      self.__OnConnected()
    except KeyboardInterrupt:
      print("Interrupted!")
      raise
    except:
      print("Failed to connect!")
      
  def Disconnect(self):
    self.Processing = False
    
    if self.__socket:
      self.__socket.close()
    
    if self.__thread:
      self.__thread.join()
  
  def SendPosition(self, direction):
    if self.Processing is False or self.__socket is None:
      print("Websocket is not connected!")
      return
      
    JsonMessage = {
      "action": direction,
      "source": "dogcamai"
    }
    
    print("Sending new postion message")
    self.__socket.send(json.dumps(JsonMessage))
  
  def __OnConnected(self):
    self.Processing = True
    if self.__thread is None:
      self.__thread = threading.Thread(target=self.__MessageThread, daemon=True, name="WSThread")
      self.__thread.start()
  
  def __MessageThread(self):
    while self.Processing:
      try:
        Message = self.__socket.recv()
        if not Message:
          time.sleep(2)
          continue
          
        print(f"Got message: {Message}")

      except websocket.WebSocketConnectionClosedException:
        print("Socket has been disconnected!")
        # self.Connect()
        break
      except KeyboardInterrupt:
        break

      time.sleep(2)
  
