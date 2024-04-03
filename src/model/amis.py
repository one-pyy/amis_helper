import asyncio as ai
import os
import random


from sqlmodel import Field, Relationship, String, Text
from sqlmodel import select, update, delete, insert
from sqlmodel.ext.asyncio.session import AsyncSession

from .base import Model

class Amis(Model, table=True):
  """amis页面存储类"""
  __tablename__ = "amis"
  id: int | None = Field(default=None, primary_key=True)
  path: str = Field(sa_type=String(256), unique=True, index=True)
  title: str = Field(sa_type=String(1024), default="")
  json: str = Field(sa_type=Text, default="")
