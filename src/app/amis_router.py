from typing import *
import os
import asyncio as ai
import pathlib

from fastapi import Query, Body, Path, Cookie, Depends
from fastapi import APIRouter, Request, Response
from fastapi import HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import delete, insert, select, update
from sqlmodel.ext.asyncio.session import AsyncSession
import httpx

from ..conf import AMIS_TEMPLATE, AMIS_EDITOR_CODE, HEADERS, APP_CONF
from ..model import Amis, commit, db_sess_dp, flush, get_sess, AmisRes, AmisExp
from ..admin import auth


CDN: List[str] = APP_CONF.cdn # type: ignore
AMIS_TEMPLATE_WITH_SDK = AMIS_TEMPLATE.replace("{%sdk_path%}", "/amis/sdk") # type: ignore


amis = APIRouter(tags=["amis"])
amis_admin = APIRouter(dependencies=[Depends(auth.requires("root")())])

pages: Dict[str, HTMLResponse] = {}
sdk: Dict[str, RedirectResponse] = {}

def make_amis_page(title: str, json: str) -> HTMLResponse:
  return HTMLResponse(AMIS_TEMPLATE_WITH_SDK
                      .replace("{%title%}", title)
                      .replace("{%json%}", json))

async def load_pages():
  async with get_sess() as sess:
    amis_results = await sess.scalars(select(Amis))
    for result in amis_results:
      pages[result.path] = make_amis_page(result.title, result.json)

async def generate_sdk():
  cli = httpx.AsyncClient(headers=HEADERS, timeout=5)
  
  async def choose_CDN(path: pathlib.Path):
    targets = [f"{url}/{path}" for url in CDN]
    ans = await ai.gather(
      *(cli.get(target) for target in targets), return_exceptions=True)
    for i, res in enumerate(ans):
      if isinstance(res, httpx.Response) and res.status_code == 200:
        sdk[str(path)] = RedirectResponse(targets[i])
  
  sdk_path = pathlib.Path("src/amis_sdk")
  paths = [path.relative_to(sdk_path) for path in sdk_path.glob("**/*")]
  await ai.gather(
    *(choose_CDN(path) for path in paths if path.is_file()))

@amis_admin.get('/path')
async def get_path(sess: AsyncSession = Depends(db_sess_dp)):
  paths = await sess.scalars(select(Amis.path))
  return {'options': [{"label": path, "value": path}
                      for path in paths]}

@amis_admin.get('/all_pages')
async def get_all_pages(sess: AsyncSession = Depends(db_sess_dp)):
  pages = await sess.scalars(select(Amis))
  return {"data": {"paths": {page.path: {"title": page.title, "json": page.json}
                              for page in pages}}}
  
@amis_admin.post('/path')
async def create_path(path: str = Body(..., embed=True), 
                      sess: AsyncSession = Depends(db_sess_dp)):
  sess.add(Amis(path=path))
  if await commit(catch_regex=r"\(1062,"):
    return AmisRes("创建成功")
  else:
    raise AmisExp("路径重复")

@amis_admin.patch('/path')
async def update_path(origin: str = Body(...), replace_as: str = Body(...), 
                      sess: AsyncSession = Depends(db_sess_dp)):
  await sess.exec(
    update(Amis).where(Amis.path==origin).values(path=replace_as))
  if await commit(catch_regex=r"\(1062,"):
    return AmisRes("修改成功")
  else:
    raise AmisExp("路径重复")

@amis_admin.delete('/path')
async def delete_path(path: str = Body(..., embed=True), 
                      sess: AsyncSession = Depends(db_sess_dp)):
  await sess.exec(
    delete(Amis).where(Amis.path==path))
  await commit(echo=True)
  pages.pop(path, None)
  return AmisRes("删除成功")

@amis_admin.post('/set_pages')
async def set_amis(path: str = Body(...), 
                   title: str = Body(...), 
                   json: str = Body(...), 
                   sess: AsyncSession = Depends(db_sess_dp)):
  # 为了兼容其实并不存在的多种数据库, 就不用upsert了
  page = await sess.scalar(
    select(Amis).filter_by(path=path))
  if page:
    page.title, page.json = title, json
  else:
    sess.add(Amis(path=path, title=title, json=json))
  if await commit(echo=True):
    pages[path] = make_amis_page(title, json)
    return AmisRes("保存成功")
  else:
    raise AmisExp("保存失败")

@amis.get('/pages/{path:path}')
async def get_amis_page(path: str = Path(...)):
  return pages.get(path, Response(status_code=404))

@amis.get('/sdk/{path:path}')
async def get_js(path: str = Path(...)):
  return sdk.get(path, RedirectResponse(f"/static/amis_sdk/{path}"))

# @amis_admin.get("/set_pages")
# def set_amis_HTML_page():
#   return make_amis_page(*AMIS_EDITOR_CODE)


amis.include_router(amis_admin)
