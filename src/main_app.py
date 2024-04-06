from asyncio import gather
import os
import traceback
from typing import *
import logging as lg
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, JSONResponse

from .app import amis, startup as app_startup
from .model import AmisExp, AmisRes, create_all_tables, close_engine
from .utils import patch_asyncio_event_loop, add_log_for_all
from .conf import ROOT_DIR
from .conf import APP_CONF
from .admin import site as admin_site, auth, admin_startup

patch_asyncio_event_loop()

INDEX_PATH: str = os.path.join('/amis/pages/', APP_CONF.index_path)
LOG_OPTIONS: dict = APP_CONF.log
DEBUG: bool = APP_CONF.debug

# 很不幸, 似乎get_route_handler要放在注册api的前面...
# 之前就吐槽过ejs, 没想到fastapi也这样, 无语耶
# 于是就有了这个猴子补丁
# 另外还有一份exp名单
if LOG_OPTIONS.log_all:
  add_log_for_all(LOG_OPTIONS.ignore_headers)

@asynccontextmanager
async def lifespan(app: FastAPI):
  await create_all_tables(drop_exist=True)
  await gather(app_startup(), admin_startup())
  yield
  await close_engine()

app = FastAPI(docs_url="/docs" if DEBUG else None, 
              redoc_url="/redoc" if DEBUG else None,
              openapi_url = "/openapi.json" if DEBUG else None,
              debug=DEBUG,
              lifespan=lifespan)

app.mount("/static/amis_sdk", 
          StaticFiles(directory=ROOT_DIR/"amis_sdk"), name="amis_sdk")
app.include_router(amis, prefix="/amis")
admin_site.mount_app(app)

if INDEX_PATH:
  @app.get('/')
  async def root():
    return RedirectResponse(INDEX_PATH)

@app.exception_handler(AmisExp)
async def amis_exp_handler(request: Request, exc: AmisExp):
  return AmisRes(exc.msg, exc.data, exc.status, exc.msg_timeout)
