from .utils import patch_asyncio_event_loop, run_sync
from .sql import create_all_tables
patch_asyncio_event_loop()
run_sync(create_all_tables(drop_exist=True))

from typing import *
import os

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse

from .app import amis
from .conf import read_conf
from .model import AmisExp, AmisRes

APP_CONF = read_conf("app")
INDEX_PATH: str = os.path.join('/amis/pages/', APP_CONF['index_path']) # type: ignore

app = FastAPI()
app.include_router(amis, prefix="/amis")

if INDEX_PATH:
  @app.get('/')
  async def root():
    return RedirectResponse(INDEX_PATH)

@app.exception_handler(AmisExp)
async def unicorn_exception_handler(request: Request, exc: AmisExp):
  amis_res = AmisRes(status = exc.status, msg = exc.msg, msgTimeout = exc.msg_timeout, data = exc.data)
  return JSONResponse(amis_res.dict())
