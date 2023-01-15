from typing import *
import os

import regex as re
from fastapi import Query, Body, Path, Cookie, Depends
from fastapi import APIRouter, FastAPI, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi import HTTPException
from objprint import op
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..conf import AMIS_TEMPLATE, SET_AMIS, read_conf
from ..model import AmisRes
from ..sql import Amis, commit, db_sess, flush, get_session
from ..utils import run_sync


CONF = read_conf("amis")
AMIS_PASSWORD: str = CONF['password'] # type: ignore
AMIS_TEMPLATE_WITH_CDN = AMIS_TEMPLATE.replace("{%CDN%}", CONF['cdn']) # type: ignore


async def amis_check(amis_pass: str = Cookie("")):
  if amis_pass != AMIS_PASSWORD:
    raise HTTPException(status_code=404)

amis = APIRouter(tags=["amis"])
amis_admin = APIRouter(dependencies=[Depends(amis_check)])

pages: Dict[str, HTMLResponse] = {}

def make_amis_page(title: str, json: str) -> HTMLResponse:
  return HTMLResponse(AMIS_TEMPLATE_WITH_CDN
                      .replace("{%title%}", title)
                      .replace("{%json%}", json))

async def load_pages():
  sess = get_session()
  amis_results = await sess.scalars(select(Amis))
  for result in amis_results:
    pages[result.path] = make_amis_page(result.title, result.json)

run_sync(load_pages())

@amis_admin.get('/path')
async def get_path(sess: AsyncSession = Depends(db_sess)):
  paths = await sess.scalars(select(Amis.path))
  return {'options': [{"label": path, "value": path}
                      for path in paths]}

@amis_admin.get('/all_pages')
async def get_all_pages(sess: AsyncSession = Depends(db_sess)):
  pages = await sess.scalars(select(Amis))
  return {"data": {"paths": {page.path: {"title": page.title, "json": page.json}
                              for page in pages}}}
  
@amis_admin.post('/path')
async def create_path(path: str = Body(..., embed=True), 
                    sess: AsyncSession = Depends(db_sess)):
  sess.add(Amis(path=path))
  if await commit(catch_regex=r"\(1062,"):
    return AmisRes(msg="创建成功")
  else:
    return AmisRes(status=1, msg="路径重复")

@amis_admin.patch('/path')
async def update_path(origin: str = Body(...), replace_as: str = Body(...), 
                      sess: AsyncSession = Depends(db_sess)):
  await sess.execute(
    update(Amis).where(Amis.path==origin).values(path=replace_as))
  if await commit(catch_regex=r"\(1062,"):
    return AmisRes(msg="修改成功")
  else:
    return AmisRes(status=1, msg="路径重复")

@amis_admin.delete('/path')
async def delete_path(path: str = Body(..., embed=True), 
                      sess: AsyncSession = Depends(db_sess)):
  await sess.execute(
    delete(Amis).where(Amis.path==path))
  await commit(echo=True)
  pages.pop(path, None)
  return AmisRes(msg = "删除成功")

@amis_admin.post('/set_pages')
async def set_amis(path: str = Body(...), title: str = Body(...), json: str = Body(...),
                    sess: AsyncSession = Depends(db_sess)):
  # 为了兼容其实并不存在的多种数据库, 就不用upsert了
  page = await sess.scalar(
    select(Amis).filter_by(path=path))
  if page:
    page.title, page.json = title, json
  else:
    sess.add(Amis(path=path, title=title, json=json))
  if await commit(echo=True):
    pages[path] = make_amis_page(title, json)
    return AmisRes(msg="保存成功")
  else:
    return AmisRes(status=1, msg="未知错误")

@amis.get('/pages/{path:path}')
async def get_amis_page(path: str = Path(...)):
  return pages.get(path, Response(status_code=404))

@amis_admin.get("/set_pages")
def set_amis_HTML_page():
  return make_amis_page(*SET_AMIS)

amis.include_router(amis_admin)
