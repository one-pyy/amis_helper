from typing import *

from pydantic import BaseModel

class AmisRes(BaseModel):
  """amis返回类"""
  status: int = 0
  msg: str = ""
  msgTimeout: int = 5000
  data: Union[None, BaseModel] = None


class AmisExp(Exception):
  """amis异常类"""
  def __init__(self, status: int = 1, msg: str = "", msg_timeout: int = 5000, data: Union[None, BaseModel] = None):
    self.status = status
    self.msg = msg
    self.msg_timeout = msg_timeout
    self.data = data
