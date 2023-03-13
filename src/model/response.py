from typing import *

from pydantic import BaseModel

class AmisRes(BaseModel):
  """amis返回类"""
  status: int
  msg: str
  msg_timeout: int
  data: Any
  
  def __init__(self, 
               msg: str = "", 
               data: Any = None, 
               status: int = 0, 
               msg_timeout: int = 5000):
    super().__init__(status=status, msg=msg, msg_timeout=msg_timeout, data=data)

class AmisExp(Exception):
  """amis异常类"""
  def __init__(self, 
               msg: str = "", 
               data: Any = None,
               status: int = 1, 
               msg_timeout: int = 5000):
    self.status = status
    self.msg = msg
    self.msg_timeout = msg_timeout
    self.data = data
