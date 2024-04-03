from pitricks.utils import make_parent_top, print_exc, acatch_exp
make_parent_top(2)

import re
import traceback
from contextvars import ContextVar
from typing import *

from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from ..conf import read_sql_conf
from ..utils import kwargs_to_dict

SQL_CONF = read_sql_conf()

async_scoped_session: ContextVar[Optional[AsyncSession]] = ContextVar('async_scoped_session', default=None)

engine=create_async_engine(SQL_CONF['url'], echo=SQL_CONF['debug'], )
sessionMaker = async_sessionmaker(
  bind=engine, class_=AsyncSession, 
  expire_on_commit=False)



def get_sess(**kwargs) -> AsyncSession:
  """获取单个协程的session"""
  if (sess:=async_scoped_session.get()) is None:
    sess=sessionMaker(**kwargs)
    async_scoped_session.set(sess)
  assert isinstance(sess, AsyncSession), f'async_scoped_session.get() returned {type(sess)} but not AsyncSession'
  # print(id(sess))
  return sess

async def close_session():
  sess=async_scoped_session.get()
  if sess is not None:
    await sess.close()
    async_scoped_session.set(None)

async def db_sess_dp():
  db = get_sess()
  try:
    yield db
    if db.dirty: # 获取是否有修改
      await db.commit()
  except Exception as e:
    await db.rollback()
    print_exc()
  finally:
    await close_session()


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
  sess=get_sess()
  return not (await acatch_exp(sess.commit(), failed_return=True, **kwargs))
  

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
  sess=get_sess()
  return not (await acatch_exp(sess.flush(), failed_return=True, **kwargs))


async def create_all_tables(drop_exist = False):
  async with engine.begin() as conn:
    if drop_exist:
      await conn.run_sync(SQLModel.metadata.drop_all)
    await conn.run_sync(SQLModel.metadata.create_all)
  await engine.dispose()


async def close_engine():
  await engine.dispose()


class Model(SQLModel):
  
  def update(self, model: 'Model | dict', 
             *,
             exclude_unset=True,
             update: dict[str, Any] | None = None):
    if isinstance(model, dict):
      return self.sqlmodel_update(model, update=update)
    else:
      return self.sqlmodel_update(
        model.model_dump(exclude_unset=exclude_unset), update=update)