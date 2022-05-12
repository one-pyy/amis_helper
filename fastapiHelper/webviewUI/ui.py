import webview
import threading
import uvicorn
from random import randint
import socket
import uuid

def getIdlePort()->int:
  for i in range(233333):
    port=randint(5000,65535)
    try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        s.connect(('127.0.0.1',port))
    except Exception:
      return port
  raise RuntimeError("No idle port found")

def start_ui(app,title=uuid.uuid1()):
  port=getIdlePort()
  threading.Thread(target=uvicorn.run, args=(app,),kwargs={"host":"127.0.0.1","port":port}, daemon=True).start()
  webview.create_window('Hello world', f'http://127.0.0.1:{port}')
  webview.start()
