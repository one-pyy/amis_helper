import os
import uvicorn

from src.conf import read_conf, ROOT_DIR

MAIN_CONF = read_conf("main")
APP_CONF = read_conf("app")

USE_GUI: bool = MAIN_CONF['use_GUI'] # type: ignore
PORT: int = MAIN_CONF['port'] # type: ignore
WORKER_NUM: int = MAIN_CONF['worker_num'] # type: ignore
DEBUG: bool = APP_CONF['debug'] # type: ignore

def run_server(port: int = PORT):
  (ROOT_DIR/"log").mkdir(exist_ok=True) # type: ignore
  
  uvicorn.run(
    "src.main_app:app", 
    host="127.0.0.1" if USE_GUI else "0.0.0.0", 
    port=port, 
    reload=DEBUG, 
    log_config="src/conf/log.yaml",
    access_log=False, 
    workers=None if DEBUG else WORKER_NUM,
  )

if __name__ == '__main__':
  if USE_GUI:
    from src.utils import start_GUI, get_idle_port
    from threading import Thread
    port = get_idle_port()
    Thread(target=run_server, 
           args=(port,), 
           daemon=True).start()
    start_GUI(port)
  else:
    os.system(f"start http://127.0.0.1:{PORT}")
    run_server()
