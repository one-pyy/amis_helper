import asyncio as ai
import os
import random
from typing import *

import regex as re
from fastapi import APIRouter, Body, FastAPI, Path, Request, Response, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from objprint import op
# from async_property import async_cached_property
from sqlalchemy import Column, Enum, ForeignKey, Index, UniqueConstraint
from sqlalchemy import select, update, delete, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.orm import DeclarativeBase, Query, WriteOnlyMapped, backref, relationship
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import Boolean, Integer, String, Text
from async_lru import alru_cache

from .base import Base, commit, flush, get_session, create_all_tables, db_sess
from ..conf import AMIS_TEMPLATE, SET_AMIS, read_conf
from ..model import ResAmis

CONF = read_conf("amis")
AMIS_CDN: str = CONF['cdn'] # type: ignore
AMIS_PASSWORD: str = CONF['password'] # type: ignore
INDEX_PATH: str = CONF['index_path'] # type: ignore

AMIS_TEMPLATE_WITH_CDN = AMIS_TEMPLATE.replace("{%CDN%}", AMIS_CDN)

class Amis(Base):
  """amis页面存储类"""
  __tablename__ = "amis"
  __mapper_args__ = {"eager_defaults": True}
  id: Mapped[int] = mapped_column(primary_key=True)
  path: Mapped[str] = mapped_column(String(256), unique=True, index=True)
  title: Mapped[str] = mapped_column(String(1024), nullable=True)
  json: Mapped[str] = mapped_column(Text, nullable=True)
  
  @staticmethod
  async def start(app: FastAPI):
    api=APIRouter()
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
    
    await load_pages()
    
    if AMIS_PASSWORD:
      @app.middleware("http")
      async def amis_check(request: Request, call_next):
        if re.match('^/amis/(?!pages/)', request.url.path) and request.cookies.get('amis_pass')!=AMIS_PASSWORD:
          return Response(status_code=404)
        response = await call_next(request)
        return response
    
    if INDEX_PATH:
      @app.get('/')
      async def root():
        return RedirectResponse(os.path.join('/amis/pages/', INDEX_PATH))
    
    @api.get('/path')
    async def get_path(sess: AsyncSession = Depends(db_sess)):
      paths = await sess.scalars(select(Amis.path))
      return {'options': [{"label": path, "value": path}
                          for path in paths]}
    
    @api.get('/all_pages')
    async def get_all_pages(sess: AsyncSession = Depends(db_sess)):
      pages = await sess.scalars(select(Amis))
      return {"data": {"paths": {page.path: {"title": page.title, "json": page.json}
                                 for page in pages}}}
      
    @api.post('/path')
    async def create_path(path: str = Body(..., embed=True), 
                       sess: AsyncSession = Depends(db_sess)):
      sess.add(Amis(path=path))
      if await commit(catch_regex=r"\(1062,"):
        return ResAmis(msg="创建成功")
      else:
        return ResAmis(status=1, msg="路径重复")

    @api.patch('/path')
    async def update_path(origin: str = Body(...), replace_as: str = Body(...), 
                          sess: AsyncSession = Depends(db_sess)):
      await sess.execute(
        update(Amis).where(Amis.path==origin).values(path=replace_as))
      if await commit(catch_regex=r"\(1062,"):
        return ResAmis(msg="修改成功")
      else:
        return ResAmis(status=1, msg="路径重复")

    @api.delete('/path')
    async def delete_path(path: str = Body(..., embed=True), 
                          sess: AsyncSession = Depends(db_sess)):
      await sess.execute(
        delete(Amis).where(Amis.path==path))
      await commit(echo=True)
      pages.pop(path, None)
      return ResAmis(msg = "删除成功")

    @api.post('/set_pages')
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
        return ResAmis(msg="保存成功")
      else:
        return ResAmis(status=1, msg="未知错误")
    
    @api.get('/pages/{path:path}')
    async def get_amis_page(path: str = Path(...)):
      return pages.get(path, Response(status_code=404))

    @api.get("/set_pages")
    def set_amis_HTML_page():
      return make_amis_page(*SET_AMIS)
    
    app.include_router(api, prefix='/amis', tags=['amis'])
