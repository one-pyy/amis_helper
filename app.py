from amisHelper import startAmis
from fastapi import FastAPI

app=FastAPI()
startAmis(app,"/amis/set")
