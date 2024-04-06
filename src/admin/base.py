import os

# from fastapi_amis_admin.admin.site import AdminSite
from fastapi_amis_admin.admin import (IframeAdmin, ModelAction, ModelAdmin,
                                      PageAdmin, AdminApp)
from fastapi_amis_admin.admin.settings import Settings
from fastapi_amis_admin.amis.components import Page, PageSchema

from fastapi_user_auth.auth import Auth
from fastapi_user_auth.auth.backends.jwt import JwtTokenStore

from ..conf import SQL_CONF, APP_CONF
from .base_AuthAdminSite import MyAdminSite

# from ..model import engine


JWT_SECRET: str = os.environ['jwt_secret']

site = MyAdminSite(
  Settings(
    site_title = "管理平台", 
    site_path = "/admin",
    amis_pkg = "amis@6.3.0",
    database_url_async = SQL_CONF.url,
    version="0.0.1",
    debug=SQL_CONF.debug,
  ),
)

auth = site.auth = Auth(
  db=site.auth.db, 
  token_store=JwtTokenStore(JWT_SECRET, expire_seconds=365*86400)
)


