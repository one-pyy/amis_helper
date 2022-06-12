import webview
import threading
import uvicorn
from random import randint
import socket
import uuid

def getIdlePort()->int:
  begin, end= 5000, 60000
  sub=end-begin
  base=randint(0, sub)
  for i in range(0,sub):
    port=(base+i)%sub+begin
    try:
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.1)
        s.connect(('127.0.0.1',port))
    except Exception:
      return port
  raise RuntimeError("No idle port found")

def start_ui(app,title=None,**kwargs):
  """
  width: int = 800, height: int = 600, x: Unknown | None = None, y: Unknown | None = None, resizable: bool = True, fullscreen: bool = False, min_size: Unknown = (200, 100), hidden: bool = False, frameless: bool = False, easy_drag: bool = True, minimized: bool = False, on_top: bool = False, confirm_close: bool = False, background_color: str = '#FFFFFF', transparent: bool = False, text_select: bool = False, localization: Unknown | None = None
  """
  title=title or str(uuid.uuid1())
  port=getIdlePort()
  threading.Thread(target=uvicorn.run, args=(app,),kwargs={"host":"127.0.0.1","port":port}, daemon=True).start()
  webview.create_window(title, f'http://127.0.0.1:{port}', **kwargs)
  webview.start()
