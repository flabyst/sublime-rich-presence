import os

from sublime import (
  load_settings,
  set_timeout_async,
  active_window
)

from .rpc import Client
from sublime_plugin import ApplicationCommand

from os import path
from time import time

def plugin_loaded():
  global client
  global settings

  settings = load_settings("Rich Presence.sublime-settings")
  client = Client(settings.get("client_id"))

  try:
    client.connect()
    set_timeout_async(lambda: update_activity(), 1000)
  except Exception as e:
    print(e)

def plugin_unloaded():
  global client
  global settings

  try:
    client.disconnect()

    del client
    del settings
  except:
    None

def update_activity():
  global client
  global settings

  activity = { "details": "Idle" }
  window = active_window()

  variables = window.extract_variables()
  view = window.active_view()

  folders = [
    path.basename(value)
      for value in window.folders()
  ]

  exclude_folders = settings.get("exclude_folders")
  file_name = variables.get("file_name")

  if folders:
    for value in exclude_folders:
      folders.remove(value)\
        if value in folders else None

    if len(folders):
      activity["state"] =\
        "Working on %s" % (", ".join(folders))

  if file_name or view.name():
    activity["details"] =\
      "Editing %s" % ("a buffer" if view.name() else file_name)

  try:
    client.send(1, {
      "cmd": "SET_ACTIVITY",
      "nonce": "%s" % time(),
      "args": {
        "activity": activity,
        "pid": os.getpid()
      }
    })

    set_timeout_async(lambda: update_activity(),
      settings.get("update_activity_delay") * 1000)
  except Exception as e:
    print(e)

class ConnectCommand(ApplicationCommand):
  def run(self):
    set_timeout_async(lambda: plugin_loaded())

class DisconnectCommand(ApplicationCommand):
  def run(self):
    set_timeout_async(lambda: plugin_unloaded())
