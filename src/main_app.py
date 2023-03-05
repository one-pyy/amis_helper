import os
import traceback
from typing import *
import logging

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse

from .app import amis
from .model import AmisExp, AmisRes
from .conf import ROOT_DIR
from .utils import patch_asyncio_event_loop, add_log_for_all
from .sql import create_all_tables
from .conf import read_conf

patch_asyncio_event_loop()

APP_CONF = read_conf("app")
INDEX_PATH: str = os.path.join('/amis/pages/', APP_CONF['index_path']) # type: ignore
LOG_ALL: bool = APP_CONF['log_all'] # type: ignore

# 很不幸, 似乎get_route_handler要放在注册api的前面...
# 之前就吐槽过ejs, 没想到fastapi也这样, 无语耶
# 于是就有了这个猴子补丁
if LOG_ALL:
  add_log_for_all()

app = FastAPI()

@app.on_event("startup")
async def create_table():
  await create_all_tables(drop_exist=False)

app.mount("/static/amis_sdk", StaticFiles(directory=ROOT_DIR/"amis_sdk"), name="amis_sdk")
app.include_router(amis, prefix="/amis")

if INDEX_PATH:
  @app.get('/')
  async def root():
    return RedirectResponse(INDEX_PATH)

@app.exception_handler(AmisExp)
async def unicorn_exception_handler(request: Request, exc: AmisExp):
  amis_res = AmisRes(status = exc.status, msg = exc.msg, msgTimeout = exc.msg_timeout, data = exc.data)
  return JSONResponse(amis_res.dict())
