"使用fastapi_amis_admin创建管理平台, fastapi_user_auth创建用户权限系统; 外面的amis page用于构筑用户页面, 里面的admin page用于构筑管理页面"
# 运行一下需要的patch
from ._patch import _patch
_patch()
del _patch

# 运行一遍pages.py, 以注册页面
from . import pages
del pages


from .base import site, auth

async def admin_startup():
  await auth.create_role_user("admin")
  await auth.create_role_user("root")
  
  await site.router.startup()
  
  #Add a default casbin rule
  if not auth.enforcer.enforce("u:admin", site.unique_id, "page", "page"):
    await auth.enforcer.add_policy("u:admin", site.unique_id, "page", "page", "allow")