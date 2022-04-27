from fastapi import Body, FastAPI, Path, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from .. import sql
import os

__all__ = ["startAmis"]

def startAmis(app:FastAPI, defaultPath=None):
  sql.set("create table if not exists amis(path text unique,title text default '',json text default '')")
  #app.mount("/amis/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__),'amis')), name="amis")

  def amisLoad(title:str, json:str):
    from .amisTemplate import amisTemplate
    return amisTemplate.replace('{%title%}',title).replace('{%json%}',json).replace('{%CDN%}',"https://cdn.staticfile.org/amis/1.8.0")
  
  if defaultPath!=None:
    @app.get('/')
    def root():
      return RedirectResponse('/amis/get/'+defaultPath)
  
  @app.get('/amis/getPath')
  def getPath():
    return {'options':[{"label":each[0],"value":each[0]} for each in sql.get("select path from amis")]}
  
  # @app.get('/amis/getByPath')
  # def getByPath(path:str=Body(...,embed=True)):
  #   ans=sql.get("select title,json from amis where path=??",path)
  #   return {"data":{"rows":{"title":ans[0],"json":ans[1]}}}
  
  @app.get('/amis/getAll')
  def getAll():
    ans=sql.get("select path,title,json from amis")
    return {"data":{"paths":{each[0]:{"title":each[1],"json":each[2]} for each in ans}}}
    
  @app.post('/amis/newPath')
  def newPath(path:str=Body(...,embed=True)):
    if sql.set("insert into amis(path) values(??)",path):
      return Response(status_code=201)
    else:
      return Response(status_code=422)

  @app.post('/amis/updatePath')
  def updatePath(origin:str=Body(...), replace_as:str=Body(...)):
    if sql.set("update amis set path=?? where path=??",replace_as,origin):
      return Response(status_code=201)
    else:
      return Response(status_code=422)

  @app.post('/amis/deletePath')
  def deletePath(path:str=Body(...,embed=True)):
    if sql.set("delete from amis where path=??",path):
      return Response(status_code=204)
    else:
      return Response(status_code=422)

  @app.post('/amis/set')
  def setAmis(path:str=Body(...), title:str=Body(...), json:str=Body(...)):
    if sql.set("insert into amis values(??,??,??)",path,title,json, echo=False) or sql.set("update amis set title=??,json=?? where path=??",title,json,path, echo=False):
      return Response(status_code=201)
    else:
      return Response(status_code=422)
  
  @app.get('/amis/get/{path:path}')
  def getAmis(path:str=Path(...)):
    context=sql.get("select title,json from amis where path=??",path)
    if context.__len__()==0:
      return Response(status_code=404)
    return HTMLResponse(amisLoad(context[0][0],context[0][1]))

  @app.get("/amis/set")
  def setAmisHTML():
    from .amisTemplate import setAmis
    return HTMLResponse(amisLoad(setAmis[0],setAmis[1]))
