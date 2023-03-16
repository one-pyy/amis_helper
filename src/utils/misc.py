import sys
import random
from typing import *
import asyncio as ai


def get_upper_kwargs(level=1) -> Dict[str, Any]:
  """ 获取上x层的变量, 但是请不要修改它 """
  return sys._getframe(level+1).f_locals


def kwargs_to_dict() -> Dict[str, Any]:
  """ 获取本层传入了什么, 于是你可以把它传给下一层 """
  kwargs = get_upper_kwargs(0)
  return kwargs


def get_random_str(length=10, 
                   mode: Literal["all", "digit", "lower", "upper", "letter", "word", "url"]="all"):
  """ 生成一个指定长度的随机字符串 """
  
  dic={
    "digit": """0123456789""",
    "lower": """abcdefghijklmnopqrstuvwxyz""",
    "upper": """ABCDEFGHIJKLMNOPQRSTUVWXYZ""",
    "letter": """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ""",
    "word": """abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789""",
    "url": """-_.!~*'()abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789""",
    "all": R"""!"#$%&'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\]^_`abcdefghijklmnopqrstuvwxyz{|}~ """,
  }
  str_list =[random.choice(dic[mode]) for _ in range(length)]
  return ''.join(str_list)


def run_sync(async_func: Union[Awaitable, Iterable[Awaitable]]):
  if isinstance(async_func, Iterable):
    async def run_gather():
      return await ai.gather(*async_func)
    async_func = run_gather()
  loop = ai.get_event_loop()
  return loop.run_until_complete(async_func)


def patch_asyncio_event_loop():
  import nest_asyncio
  nest_asyncio.apply()


def add_log_for_all(ignore_headers: List[str]):
  import logging
  import re
  try:
    import pretty_errors
    print_exc = lambda: pretty_errors.excepthook(*sys.exc_info())
  except:
    import traceback
    print_exc = lambda: traceback.print_exc()
  
  from fastapi.routing import APIRoute
  from fastapi import Request
  from rich.markup import escape
  
  def wrap_color(target: str, color: str = "orange1"):
    return f"\\[[bold {color}]{target}[/bold {color}]]"
  
  origin_get_route_handler = APIRoute.get_route_handler
  def get_route_handler(self):
    async def log_all(request: Request):
      ip = "unknown ip" if request.client is None else request.client.host
      log_content = [
        "="*50,
        wrap_color("ip")+" "+ip,
        f"\\[{request.method}] {request.url._url}",
        wrap_color("Headers"),
        *([escape(f"    {k}: {v}") 
            for k, v in request.headers.items() 
            if k != 'cookie' and k not in ignore_headers] 
          or ["    All headers are ignored"]),
      ]
      if request.cookies:
        log_content+=[
          wrap_color("Cookies"),
          *[escape(f"    {k}: {v}") for k, v in request.cookies.items()]]
      body = (await request.body()).decode(errors="xmlcharrefreplace")
      if body:
        log_content.append(wrap_color("Body"))
        log_content.append(escape(body if len(body) < 1000 else body[:1000] + f"...[{len(body)}]"))
      
      logging.info("\n".join(log_content))
      return await origin_get_route_handler(self)(request)
    
    return log_all
  
  APIRoute.get_route_handler = get_route_handler


