from pathlib import Path
import sys
from typing import Any

import json5 as json
from objprint import op


def pwd() -> Path:
  path = sys._getframe(1).f_locals['__file__']
  return Path(path).parent


CONF_DIR: Path = pwd()
ROOT_DIR: Path = pwd().parent


def _parse(path) -> dict[str, Any]:
  return json.load(open(path, encoding='utf-8')) # type: ignore


def read_conf(filename) -> dict[str, Any]:
  """输入配置文件名(可省略.json5)或路径, 返回配置文件内容"""
  path: Path = CONF_DIR/filename
  if path.suffix == '.json5':
    return _parse(path)
  return _parse(path.with_suffix('.json5'))


def read_sql_conf(which_db = None) -> dict[str, Any]:
  main_conf = read_conf("main")
  sql_conf = read_conf('sql')
  sql_conf["url"] = sql_conf["url"][which_db or main_conf['default_sql']]
  return sql_conf # type: ignore
