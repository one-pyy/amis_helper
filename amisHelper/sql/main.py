from sqlite3 import connect
from typing import *
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import re, functools
import traceback
from ..config import SQL_url,echo

# echo=True表示引擎将用repr()函数记录所有语句及其参数列表到日志
engine = create_engine(
  SQL_url, encoding='utf8', echo=echo
)

# SQLAlchemy中，CRUD是通过会话进行管理的，所以需要先创建会话，
# 每一个SessionLocal实例就是一个数据库session
# flush指发送到数据库语句到数据库，但数据库不一定执行写入磁盘
# commit是指提交事务，将变更保存到数据库文件中
_session_local = sessionmaker(autocommit=True, autoflush=True, bind=engine)

_session = _session_local()
# 创建基本映射类
# SqlBase = declarative_base()

def mul_replace(text:str, dic:Dict[str,str])->str:
  def lbd(match):
    return dic[match.group(0)]
  return re.sub('|'.join(map(re.escape, dic)), lbd, text)

def _filter(input, binds:List, fuzzy:bool)->str:
  if fuzzy:
    input = "".join(['%', str(input), '%'])
  binds.append(input)
  return f" :{len(binds)} "

def _table_filter(input, _)->str:
  return "".join([' `', mul_replace(str(input), {'`':'\\`',':':'\\:'}), '` '])

def _sql_exec(sentence:str, *args)->sqlalchemy.engine.CursorResult:
  sentence=sentence.replace(":","\\:")
  func: Dict[str, Callable[[Any, List],str]]={
    '??': functools.partial(_filter,fuzzy=False),
    '?l?': functools.partial(_filter,fuzzy=True),
    '?t?': _table_filter
  }
  binds=[]
  ls=re.split('(?<=[^\\\\])(\\?.*?\\?)',sentence)
  for i in range(1,len(ls),2):
    ls[i]=func[ls[i]](args[i//2], binds)
  return _session.execute("".join(ls), dict(zip(map(str, range(1,len(binds)+1)),binds)))

def get(sentence:str, *args)-> List[sqlalchemy.engine.Row]:
  ret=_sql_exec(sentence,*args).all()
  return ret

def get_row(sentence:str, *args)-> Union[sqlalchemy.engine.Row,None]:
  ret=_sql_exec(sentence,*args).first()
  return ret

def get_one(sentence:str, *args)-> Union[Any, None]:
  ret=get_row(sentence,*args)
  if ret is None:
    return None
  return ret[0]

def get_dict(sentence:str, *args)-> List[Dict[str,Any]]:
  return [row._asdict() for row in get(sentence,*args)]  # type: ignore

def exist(sentence:str, *args)-> bool:
  return get_row(sentence,*args) is not None

def set(sentence:str, *args, echo: bool=False)-> bool:
  try:
    _sql_exec(sentence,*args)
    return True
  except Exception as e:
    if echo==True:
      traceback.print_exc()
    return False
