from typing import *
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker
import re, functools
from ..config import SQL_url,echo
import traceback

# echo=True表示引擎将用repr()函数记录所有语句及其参数列表到日志
engine = create_engine(
  SQL_url, encoding='utf8', echo=echo
)

# SQLAlchemy中，CRUD是通过会话进行管理的，所以需要先创建会话，
# 每一个SessionLocal实例就是一个数据库session
# flush指发送到数据库语句到数据库，但数据库不一定执行写入磁盘
# commit是指提交事务，将变更保存到数据库文件中
SessionLocal = sessionmaker(autocommit=True, autoflush=True, bind=engine)

session = SessionLocal()
# 创建基本映射类
# SqlBase = declarative_base()

def mulReplace(text:str, dic:Dict[str,str])->str:
  def lbd(match):
    return dic[match.group(0)]
  return re.sub('|'.join(map(re.escape, dic)), lbd, text)

def filter(input, binds:Dict[str, Any], fuzzy:bool)->str:
  if isinstance(input,bool):
    return "".join([' ',str(input),' '])
  elif input is None:
    return ' null '
  elif isinstance(input,bytes):
    index=len(binds)
    binds[str(index)]=input
    return f" (:{index}) "
  ans=str(input)
  if fuzzy:
    ans="".join(['%',ans,'%'])
  return "".join([" ('",ans.replace("'","''"),"') "])

def tableFilter(input, _)->str:
  return "".join([' `',str(input).replace('`','``'),'` '])

def _sqlExec(sentence:str, *args)->sqlalchemy.engine.CursorResult:
  sentence=sentence.replace(":","\\:")
  func: Dict[str, Callable[[Any, Dict[str,Any]],str]]={
    '??': functools.partial(filter,fuzzy=False),
    '?l?': functools.partial(filter,fuzzy=True),
    '?t?': tableFilter
    }
  binds:Dict[str,Any]={}
  ls=re.split('(?<=[^\\\\])(\\?.*?\\?)',sentence)
  for i in range(1,len(ls),2):
    ls[i]=func[ls[i]](args[i//2], binds)
  return session.execute("".join(ls),binds)

def get(sentence:str, *args)-> List[sqlalchemy.engine.Row]:
  ret=_sqlExec(sentence,*args).all()
  return ret

def getRow(sentence:str, *args)-> Union[sqlalchemy.engine.Row,None]:
  ret=_sqlExec(sentence,*args).first()
  return ret

def getOne(sentence:str, *args)-> Union[Any, None]:
  ret=getRow(sentence,*args)
  if ret is None:
    return None
  return ret[0]

def exist(sentence:str, *args)-> bool:
  return getRow(sentence,*args) is not None

def getDict(sentence:str, *args)-> List[Dict[str,Any]]:
  return [row._asdict() for row in get(sentence,*args)]  # type: ignore

def set(sentence:str, *args, echo: bool=False)-> bool:
  try:
    session.execute(_sqlExec(sentence,*args))
    return True
  except Exception as e:
    if echo==True:
      traceback.print_exc()
    return False
