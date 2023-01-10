from typing import *

from fastapi import FastAPI
from src.sql import Amis, create_all_tables
from src.utils import run_sync, patch_asyncio

patch_asyncio()

app = FastAPI()
run_sync(create_all_tables(drop_exist=True))
run_sync(Amis.start(app))
