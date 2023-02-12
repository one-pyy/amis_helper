import os
import traceback

from .utils import patch_asyncio_event_loop, run_sync
from .sql import create_all_tables
from .conf import read_conf

patch_asyncio_event_loop()
run_sync(create_all_tables(drop_exist=False))

APP_CONF = read_conf("app")
INDEX_PATH: str = os.path.join('/amis/pages/', APP_CONF['index_path']) # type: ignore
LOG_ALL: bool = APP_CONF['log_all'] # type: ignore

# 很不幸, 似乎get_route_handler要放在注册api的前面...
# 之前就吐槽过ejs, 没想到fastapi也这样, 无语耶
# 于是就有了这个猴子补丁
if LOG_ALL:
  from fastapi.routing import APIRoute
  from rich.markup import escape
  origin_get_route_handler = APIRoute.get_route_handler
  def get_route_handler(self):
    async def log_all(request: Request):
      log_content = [
        "="*50,
        f"\\[{request.method}] {request.url._url}",
        "\\[[bold orange1]Headers[/bold orange1]]",
        *[escape(f"    {k}: {v}") for k, v in request.headers.items() if k != 'cookie'],
        "\\[[bold orange1]Cookies[/bold orange1]]",
        *[escape(f"    {k}: {v}") for k, v in request.cookies.items()],
      ]
      
      body = (await request.body()).decode(errors="xmlcharrefreplace")
      if body:
        log_content.append("\\[[bold orange1]Body[/bold orange1]]")
        log_content.append(escape(body if len(body) < 1000 else body[:1000] + f"...[{len(body)}]"))
        
      try:
        return await origin_get_route_handler(self)(request)
      except:
        logging.error(traceback.format_exc())
        raise
      finally:
        logging.info("\n".join(log_content))
    
    return log_all
  
  APIRoute.get_route_handler = get_route_handler


from typing import *
import logging

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, JSONResponse

from .app import amis
from .model import AmisExp, AmisRes

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
