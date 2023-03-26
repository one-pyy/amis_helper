from .amis_router import amis

async def startup():
  from asyncio import gather
  from .amis_router import load_pages, generate_sdk
  
  await gather(load_pages(), generate_sdk())
