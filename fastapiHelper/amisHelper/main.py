import re
from fastapi import Body, FastAPI, Path, Request, Response, APIRouter
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .. import sql
import os
import functools

__all__ = ["startAmis"]

def startAmis(app:FastAPI, defaultPath=None, password=None):
  api=APIRouter()
  sql.set("create table if not exists amis(path text unique,title text default '',json text default '')")
  #app.mount("/amis/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__),'amis')), name="amis")
  
  def amisLoad(title:str, json:str):
    from .amisTemplate import amisTemplate
    return amisTemplate.replace('{%title%}',title).replace('{%json%}',json).replace('{%CDN%}',"https://fastly.jsdelivr.net/npm/amis@1.9.0/sdk")
  
  if password is not None:
    @app.middleware("http")
    async def amisCheck(request: Request, call_next):
      if re.match('^/amis/',request.url.path) and not re.match('^/amis/get/',request.url.path) and request.cookies.get('amisPassword')!=password:
        return JSONResponse({'msg':'Not admin!'},403)
      response = await call_next(request)
      return response
  
  if defaultPath is not None:
    @app.get('/')
    def root():
      return RedirectResponse(os.path.join('/amis/get/',defaultPath))
  
  @api.get('/getPath')
  def getPath():
    return {'options':[{"label":each[0],"value":each[0]} for each in sql.get("select path from amis")]}
  
  # @app.get('/getByPath')
  # def getByPath(path:str=Body(...,embed=True)):
  #   ans=sql.get("select title,json from amis where path=??",path)
  #   return {"data":{"rows":{"title":ans[0],"json":ans[1]}}}
  
  @api.get('/getAll')
  def getAll():
    ans=sql.get("select path,title,json from amis")
    return {"data":{"paths":{each[0]:{"title":each[1],"json":each[2]} for each in ans}}}
    
  @api.post('/newPath')
  def newPath(path:str=Body(...,embed=True)):
    if sql.set("insert into amis(path) values(??)",path):
      return Response(status_code=201)
    else:
      return Response(status_code=422)

  @api.post('/updatePath')
  def updatePath(origin:str=Body(...), replace_as:str=Body(...)):
    if sql.set("update amis set path=?? where path=??",replace_as,origin):
      return Response(status_code=201)
    else:
      return Response(status_code=422)

  @api.post('/deletePath')
  def deletePath(path:str=Body(...,embed=True)):
    if sql.set("delete from amis where path=??",path):
      return Response(status_code=204)
    else:
      return Response(status_code=422)

  @api.post('/set')
  def setAmis(path:str=Body(...), title:str=Body(...), json:str=Body(...)):
    if sql.set("insert into amis values(??,??,??)",path,title,json, echo=False) or sql.set("update amis set title=??,json=?? where path=??",title,json,path, echo=False):
      getAmis.cache_clear()
      return Response(status_code=201)
    else:
      return Response(status_code=422)
  
  @functools.lru_cache(maxsize=None)
  def getAmis(path:str=Path(...)):
    context=sql.get("select title,json from amis where path=??",path)
    if context.__len__()==0:
      return Response(status_code=404)
    return HTMLResponse(amisLoad(context[0][0],context[0][1]))
  api.get('/get/{path:path}')(getAmis)

  @api.get("/set")
  def setAmisHTML():
    from .amisTemplate import setAmis
    return HTMLResponse(amisLoad(setAmis[0],setAmis[1]))
  
  app.include_router(api, prefix='/amis', tags=['amis'])
