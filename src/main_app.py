import os
import traceback
from typing import *
import logging

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse

from .app import amis, startup as app_startup
from .model import AmisExp, AmisRes
from .conf import ROOT_DIR
from .utils import patch_asyncio_event_loop, add_log_for_all
from .sql import create_all_tables, close_engine
from .conf import read_conf

patch_asyncio_event_loop()

APP_CONF = read_conf("app")
INDEX_PATH: str = os.path.join('/amis/pages/', APP_CONF['index_path']) # type: ignore
LOG_OPTIONS: dict = APP_CONF['log'] # type: ignore

# 很不幸, 似乎get_route_handler要放在注册api的前面...
# 之前就吐槽过ejs, 没想到fastapi也这样, 无语耶
# 于是就有了这个猴子补丁
if LOG_OPTIONS['log_all']:
  add_log_for_all(LOG_OPTIONS['ignore_headers'])

app = FastAPI()
app.debug = True

@app.on_event("startup")
async def start():
  await create_all_tables(drop_exist=False)
  await app_startup()

@app.on_event("shutdown")
async def shut():
  await close_engine()

app.mount("/static/amis_sdk", StaticFiles(directory=ROOT_DIR/"amis_sdk"), name="amis_sdk")
app.include_router(amis, prefix="/amis")

if INDEX_PATH:
  @app.get('/')
  async def root():
    return RedirectResponse(INDEX_PATH)

@app.exception_handler(AmisExp)
async def unicorn_exception_handler(request: Request, exc: AmisExp):
  amis_res = AmisRes(exc.msg, exc.data, exc.status, exc.msg_timeout)
  return JSONResponse(amis_res.dict())
