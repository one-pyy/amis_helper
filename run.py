import os
import uvicorn
import secrets

from src.conf import ROOT_DIR, MAIN_CONF, APP_CONF

USE_GUI: bool = MAIN_CONF.use_GUI
DEBUG: bool = APP_CONF.debug

os.environ['jwt_secret'] = APP_CONF.jwt_secret or secrets.token_hex(32)

def run_server(port: int = MAIN_CONF.port):
  (ROOT_DIR/"log").mkdir(exist_ok=True) # type: ignore
  
  uvicorn.run(
    "src.main_app:app", 
    host="127.0.0.1" if USE_GUI else "0.0.0.0", 
    port=port, 
    reload=APP_CONF.debug, 
    log_config="src/conf/log.yaml",
    access_log=False, 
    workers=None if DEBUG else MAIN_CONF.worker_num,
    reload_excludes=['src/log', '.history']
  )

def run_GUI():
  from src.utils import start_GUI, get_idle_port
  from threading import Thread
  port = get_idle_port()
  Thread(target=run_server, 
         args=(port,), 
         daemon=True).start()
  start_GUI(port)

if __name__ == '__main__':
  if USE_GUI:
    run_GUI()
  else:
    os.system(f"start http://127.0.0.1:{MAIN_CONF.port}")
    run_server()
