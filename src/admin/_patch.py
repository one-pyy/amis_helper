from fastapi_amis_admin.admin.admin import AdminApp
from fastapi_amis_admin.amis.components import App, Tpl

async def _get_page_as_app(self, request):
  app = App()
  app.brandName = self.site.settings.site_title
  app.logo = self.site.settings.site_icon
  app.header = ''
  # app.footer = ''

  children = await self.get_page_schema_children(request)
  app.pages = [{"children": children}] if children else []
  return app

def _patch():
  AdminApp._get_page_as_app = _get_page_as_app