from .amis_router import amis

async def startup():
  from .amis_router import load_pages
  await load_pages()
