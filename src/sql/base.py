import traceback
from contextvars import ContextVar
from typing import *

import regex as re
from configparser import ConfigParser
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from ..conf import get_sql_url
from ..utils import kwargs_to_dict


async_scoped_session: ContextVar[Optional[AsyncSession]] = ContextVar('async_scoped_session', default=None)

engine=create_async_engine(get_sql_url(), echo=False, future=True)
SessionMaker = async_sessionmaker(bind=engine, class_=AsyncSession, future=True, expire_on_commit=False)



def get_session(**kwargs) -> AsyncSession:
  """获取单个协程的session"""
  if (sess:=async_scoped_session.get()) is None:
    sess=SessionMaker(**kwargs)
    async_scoped_session.set(sess)  # type: ignore
  assert isinstance(sess, AsyncSession), f'async_scoped_session.get() returned {type(sess)} but not AsyncSession'
  # print(id(sess))
  return sess

async def close_session():
  sess=async_scoped_session.get()
  if sess is not None:
    await sess.close()
    async_scoped_session.set(None)

async def db_sess():
  db = get_session()
  try:
    yield db
    await db.commit()
  except:
    await db.rollback()
  finally:
    await close_session()

async def catch_exp(coroutine: Coroutine[Any, Any, None],
                    echo=False,
                    raise_exp=False,
                    catch_classes=Exception,
                    catch_regex=".*"):
  if not isinstance(catch_classes, tuple):
    catch_classes = (catch_classes, )

  try:
    await coroutine
    return True
  except catch_classes as e:
    if raise_exp:
      raise

    if catch_regex != ".*":
      info = str(e)
      if not re.search(catch_regex, info):
        raise

    if echo:
      traceback.print_exc()

    return False


async def commit(echo=False,
                 raise_exp=False,
                 catch_classes=Exception,
                 catch_regex=".*"):
  """
  当echo为True时才会打印错误信息
  当raise_exp为True时抛出所有错误
  当捕捉到的错误不符合catch_*参数时抛出错误
  如果有捕捉到错误, 就返回False, 否则返回True
  """
  kwargs=kwargs_to_dict()
  # async with get_session() as sess:
  sess=get_session()
  return await catch_exp(sess.commit(), **kwargs)
  

async def flush(echo=False,
                raise_exp=False,
                catch_classes=Exception,
                catch_regex=".*"):
  """
  当echo为True时才会打印错误信息
  当raise_exp为True时抛出所有错误
  当捕捉到的错误不符合catch_*参数时抛出错误
  如果有捕捉到错误, 就返回False, 否则返回True
  """
  kwargs=kwargs_to_dict()
  # async with get_session() as sess:
  sess=get_session()
  return await catch_exp(sess.flush(), **kwargs)


async def create_all_tables(drop_exist = False):
  async with engine.begin() as conn:
    if drop_exist:
      await conn.run_sync(Base.metadata.drop_all)
    await conn.run_sync(Base.metadata.create_all)
  await engine.dispose()


async def close_engine():
  await engine.dispose()


class Base(DeclarativeBase):
  """创建基类, 并且允许不对应的注解"""
  __allow_unmapped__ = True
