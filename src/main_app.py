from .utils import patch_asyncio, run_sync
from .sql import create_all_tables
patch_asyncio()
run_sync(create_all_tables(drop_exist=True))

from typing import *
import os

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from .sql import Amis
from .app import amis
from .conf import read_conf

APP_CONF = read_conf("app")
INDEX_PATH: str = os.path.join('/amis/pages/', APP_CONF['index_path']) # type: ignore

app = FastAPI()
app.include_router(amis, prefix="/amis")

if INDEX_PATH:
  @app.get('/')
  async def root():
    return RedirectResponse(INDEX_PATH)
