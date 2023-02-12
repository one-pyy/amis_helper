from src.conf import read_conf

main_conf = read_conf("main")
USE_GUI: bool = main_conf['use_GUI'] # type: ignore
PORT: int = main_conf['port'] # type: ignore

if __name__ == '__main__':
  if USE_GUI:
    from src.main_app import app
    from src.utils import start_GUI
    start_GUI(app)
  else:
    import uvicorn
    import os
    os.system(f"start http://127.0.0.1:{PORT}")
    uvicorn.run("src.main_app:app", host="0.0.0.0", port=PORT, reload=True, log_config="src/conf/log.yaml")
