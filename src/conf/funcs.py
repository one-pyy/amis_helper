from pathlib import Path
import sys
from typing import *

import json5 as json
from objprint import op

def pwd() -> Path:
  path = sys._getframe(1).f_locals['__file__']
  return Path(path).parent

CONF_DIR: Path = pwd()
ROOT_DIR: Path = pwd().parent

def _parse(path) -> Union[Dict[str, Any], List[Any]]:
  return json.load(open(path, encoding='utf-8')) # type: ignore


def read_conf(filename) -> Union[Dict[str, Any], List[Any]]:
  """输入配置文件名(可省略.json5)或路径, 返回配置文件内容"""
  path: Path = CONF_DIR/filename
  if path.suffix == '.json5':
    return _parse(path)
  return _parse(path.with_suffix('.json5'))


def get_sql_url(which= None) -> str:
  main_conf = read_conf("main")
  sql_conf = read_conf('sql')
  return sql_conf[which or main_conf['default_sql']] # type: ignore
