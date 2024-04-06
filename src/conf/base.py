from collections import UserDict
from pathlib import Path
from typing import Any, overload
import sys

import json5 as json
from objprint import op
from pitricks.utils import Conf


def pwd() -> Path:
  path = sys._getframe(1).f_locals['__file__']
  return Path(path).parent


CONF_DIR: Path = pwd()
ROOT_DIR: Path = pwd().parent


def _parse(path) -> dict[str, Any]:
  return json.load(open(path, encoding='utf-8')) # type: ignore


def read_conf(filename, use_conf_dict = True) -> dict[str, Any] | Conf:
  """输入配置文件名(可省略.json5)或路径, 返回配置文件内容"""
  if not filename.endswith('.json5'):
    filename+= '.json5'
  
  path: Path = CONF_DIR/filename
  return Conf(_parse(path)) if use_conf_dict else _parse(path) 



def read_sql_conf(which_db = None, use_conf_dict = True) -> dict[str, Any] | Conf:
  conf = read_conf('sql', False)
  conf["url"] = conf["url"][which_db or conf['default_sql']]
  return Conf(conf) if use_conf_dict else conf


