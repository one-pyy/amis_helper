from typing import *

from pydantic import BaseModel

class ResAmis(BaseModel):
  """amis返回类"""
  status: int = 0
  msg: str = ""
  msgTimeout: int = 5000
  data: Union[None, BaseModel] = None
