from fastapiHelper import startAmis,sql
from fastapi import Body, FastAPI, Path, Request, Response
import uvicorn

app=FastAPI()
startAmis(app,"/amis/set")

if __name__ == '__main__':
  uvicorn.run("app:app",host="0.0.0.0",port=8080,debug=True,reload=True)
