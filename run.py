runGUI = False
port = 8080
if __name__ == '__main__':
  if runGUI:
    from app import app
    from amisHelper import start_ui
    start_ui(app)
  else:
    import uvicorn
    import os
    os.system(f"start http://127.0.0.1:{port}")
    uvicorn.run("app:app", host="0.0.0.0", port=port, debug=True, reload=True)
