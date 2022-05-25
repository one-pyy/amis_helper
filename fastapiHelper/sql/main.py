from typing import List, Tuple, Any, Dict
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import re, functools
from ..config import SQL_url,echo
import base64
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



def filter(input, fuzzy=False)->str:
  if input in [True,False]:
    return "".join([' ',str(input),' '])
  elif input is None:
    return ' null '
  elif isinstance(input,bytes):
    return "".join([" '",base64.b85encode(input).decode(),"' "])
  ans=str(input)
  if fuzzy:
    ans="".join(['%',ans,'%'])
  return "".join([" ('",ans.replace("'","''"),"') "])

def tableFilter(input)->str:
  return "".join([' `',str(input).replace('`','``'),'` '])

def _replace(sentence:str, *args)-> str:
  func={
    '??':filter,
    '?l?':functools.partial(filter,fuzzy=True),
    '?t?':tableFilter
    }
  ls=re.split('(\\?.*?\\?)',sentence)
  for i in range(1,len(ls),2):
    ls[i]=func[ls[i]](args[i//2])
  return ''.join(ls)

def get(sentence:str, *args, bytesIndex:List[int]=[])-> List[Tuple]:
  ret=session.execute(_replace(sentence,*args)).all()
  for index in bytesIndex:
    for row in ret:
      row[index]=base64.b85decode(row[index])
  return ret

def getListDict(queryFor:str, from____:str, *args, bytesIndex:List[int]=[])-> List[Dict[str,Any]]:
  """
  from____: 从from后开始的句子。
  query for: select 后 from 前的句子, 支持别名。
  """
  ans=get(f'select {queryFor} from {from____}',*args, bytesIndex=bytesIndex)
  keys=[each.split(' ').pop() for each in queryFor.split(',')]
  return [{key:each[i] for i,key in enumerate(keys)} for each in ans]

# def queryObj(cls:BaseModel, sentence, *args)->List[Any]:
#   ls=queryList(sentence,*args)
#   return [cls.parse_obj(dic) for dic in ls]

def set(sentence:str, *args, **kwargs)-> bool:
  try:
    session.execute(_replace(sentence,*args))
    return True
  except Exception as e:
    if 'echo' not in kwargs.keys() or kwargs['echo']==True:
      print('\033[31m'+str(e)+'\033[0m')
    return False
