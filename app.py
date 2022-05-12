from fastapiHelper import startAmis,sql,start_ui
from fastapi import Body, FastAPI, Path, Request, Response
import uvicorn

runGUI=False
app=FastAPI()
startAmis(app,"/amis/set")

if __name__ == '__main__':
  if runGUI: 
    start_ui(app)
  else:
    uvicorn.run("app:app",host="0.0.0.0",port=8080,debug=True,reload=True)
