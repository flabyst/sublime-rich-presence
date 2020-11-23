import socket
import json
import struct
import tempfile

from os import path
from socket import socket

class Client:
  def __init__(self, client_id):
    self.client_id = str(client_id)
    self.socket = None
    self.ipc_path = tempfile.gettempdir()

  def connect(self):
    self.socket = socket(socket.AF_UNIX, socket.SOCK_STREAM)

    for i in range(10):
      ipc_path = path.join(self.ipc_path,
        "discord-ipc-%d" % i)

      if path.exists(ipc_path):
        self.socket.connect(ipc_path)
        break

    self.send(0, {
      "client_id": self.client_id,
      "v": 1
    })

  def disconnect(self):
    self.socket.shutdown(socket.SOCK_STREAM)

  def send(self, opcode, payload):
    payload = json.dumps(payload)
    payload = payload.encode("utf-8")
    payload = struct.pack("<ii", opcode, len(payload)) + payload
    self.socket.send(payload)
