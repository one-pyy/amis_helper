"自定义一下site内容, 因为贫弱的可扩展性和可读性, 交给llm读就行"
import contextlib
from typing import Any, Callable, Dict, List, Type

from fastapi import Depends, HTTPException, Request
from fastapi_amis_admin.admin import (AdminAction, AdminApp,
                                      AutoTimeModelAdmin, FieldPermEnum,
                                      FootableModelAdmin, FormAdmin,
                                      PageSchemaAdmin, ReadOnlyModelAdmin,
                                      SoftDeleteModelAdmin)
from fastapi_amis_admin.amis.components import (Action, ActionType,
                                                ButtonToolbar, Form, Grid, 
                                                Horizontal, Html, Page,
                                                PageSchema)
from fastapi_amis_admin.amis.constants import DisplayModeEnum, LevelEnum
from fastapi_amis_admin.crud.base import SchemaUpdateT
from fastapi_amis_admin.crud.schema import BaseApiOut
from fastapi_amis_admin.utils.pydantic import model_fields
from fastapi_amis_admin.utils.translation import i18n
from fastapi_amis_admin.utils.pydantic import create_model_by_model
from fastapi_amis_admin.models.fields import Field
from fastapi_user_auth.admin import (UserAuthApp, UserLoginFormAdmin,
                                     UserRegFormAdmin)
from fastapi_user_auth.admin.actions import (CopyUserAuthLinkAction,
                                             UpdateSubDataPermAction,
                                             UpdateSubPagePermsAction,
                                             UpdateSubRolesAction)
from fastapi_user_auth.admin.site import AuthAdminSite
from fastapi_user_auth.admin.utils import (get_admin_action_options,
                                           update_casbin_site_grouping)
from fastapi_user_auth.auth import Auth
from fastapi_user_auth.auth.models import (BaseUser, CasbinRule,
                                           CasbinSubjectRolesQuery,
                                           LoginHistory, Role, User,
                                           UserRoleNameLabel)
from fastapi_user_auth.auth.schemas import SystemUserEnum, UserLoginOut
from fastapi_user_auth.mixins.admin import (AuthFieldModelAdmin,
                                            AuthSelectModelAdmin)
from pydantic import BaseModel
from sqlalchemy import select
from sqlmodel.sql.expression import Select
from starlette import status
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import NoMatchFound

from ..utils import find_base
from ..conf import APP_CONF

ALLOW_REGISTER = APP_CONF.admin_page.allow_register

def _add_form_header(body):
  return [
    Html(
      html=f'<div style="display: flex; justify-content: center; align-items: center; margin: 96px 0px 8px;">'
      f'<span style="font-size: 32px; font-weight: bold;">{APP_CONF.admin_page.title}</span></div>'
      f'<div style="width: 100%; text-align: center; color: rgba(0, 0, 0, 0.45); margin-bottom: 40px;">{APP_CONF.admin_page.description}</div>'
    ),
    Grid(columns=[{"body": [body], "lg": 4, "valign": "middle"}], align="center", valign="middle"),
  ]

class MyLoginForm(UserLoginFormAdmin):
  page = Page()
  
  async def get_form(self, request: Request) -> Form:
    form = await find_base(self, 2).get_form(request)
    buttons = []
    if ALLOW_REGISTER:
      with contextlib.suppress(NoMatchFound):
        buttons.append(
          ActionType.Link(
            actionType="link",
            link=f"{self.site.router_path}{self.app.router.url_path_for('reg')}",
            label=i18n("Sign up"),
          )
        )
    buttons.append(Action(actionType="submit", label=i18n("Sign in"), level=LevelEnum.primary))
    form.body.sort(key=lambda form_item: form_item.type, reverse=True)
    form.update_from_kwargs(
      title="登录",
      mode=DisplayModeEnum.horizontal,
      submitText=i18n("Sign in"),
      actionsClassName="p-b",
      panelClassName="",
      wrapWithPanel=True,
      horizontal=Horizontal(left=2, right=10),
      actions=[ButtonToolbar(mode="inline", buttons=buttons)]
    )
    form.redirect = request.query_params.get("redirect") or "/"
    return form

  async def get_page(self, request: Request) -> Page:
    page = await find_base(self, 2).get_page(request)
    page.body = _add_form_header(page.body)
    
    return page

class MyRegForm(UserRegFormAdmin):
  page = Page()
  
  class schema(BaseModel):
    username: str = Field(..., title='用户名', min_length=6, max_length=32)
    password: str = Field(..., title='密码', min_length=8, max_length=32)
  
  async def handle(self, request: Request, data: SchemaUpdateT, **kwargs) -> BaseApiOut[BaseModel]:  # self.schema_submit_out
    auth: Auth = request.auth
    if data.username.upper() in SystemUserEnum.__members__ or await auth.db.async_scalar(select(self.user_model).where(self.user_model.username == data.username)):
      return BaseApiOut(status=-1, msg=i18n("Username has been registered!"), data=None)
    values = data.dict(exclude={"id", "password"})
    values["password"] = auth.pwd_context.hash(data.password.get_secret_value())  # 密码hash保存
    user = self.user_model.parse_obj(values)
    try:
      auth.db.add(user)
      await auth.db.async_flush()
    except Exception as e:
      raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"Error Execute SQL：{e}",
      ) from e
    # 注册成功,设置用户信息
    token_info = self.schema_submit_out.parse_obj(user)
    token_info.access_token = await auth.backend.token_store.write_token(user.dict())
    return BaseApiOut(code=0, msg=i18n("Registered successfully!"), data=token_info)

  async def get_form(self, request: Request) -> Form:
    form = await find_base(self, 2).get_form(request)
    form.redirect = request.query_params.get("redirect") or "/"
    form.update_from_kwargs(
      title="注册",
      mode=DisplayModeEnum.horizontal,
      submitText=i18n("Sign up"),
      actionsClassName="p-b",
      panelClassName="",
      wrapWithPanel=True,
      horizontal=Horizontal(left=2, right=10),
      actions=[
        ButtonToolbar(
          mode = "inline",
          buttons=[
            ActionType.Link(
              actionType="link",
              link=f"{self.router_path}/login",
              label=i18n("Sign in"),
            ),
            Action(actionType="submit", label=i18n("Sign up"), level=LevelEnum.primary),
          ]
        )
      ],
    )

    return form

  async def get_page(self, request: Request) -> Page:
    page = await find_base(self, 2).get_page(request)
    page.body = _add_form_header(page.body)
    return page

  async def has_page_permission(self, request: Request, obj: PageSchemaAdmin = None, action: str = None) -> bool:
    return True



# 自定义用户认证应用,继承重写默认的用户认证应用
class MyAuthApp(UserAuthApp):
  UserLoginFormAdmin = MyLoginForm
  UserRegFormAdmin = MyRegForm
  
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    if not ALLOW_REGISTER:
      self.unregister_admin(self.UserRegFormAdmin)

# 自定义用户管理站点,继承重写默认的用户管理站点
class MyAdminSite(AuthAdminSite):
  UserAuthApp = MyAuthApp