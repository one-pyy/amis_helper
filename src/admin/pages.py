"用来创建管理页面"
import json

from fastapi import Request

from ..conf import AMIS_EDITOR_CODE
from .base import site
from .base import PageAdmin, IframeAdmin, AdminApp
from .base import Page, PageSchema

@site.register_admin
class AmisEditorPageAdmin(PageAdmin):
  page_schema = AMIS_EDITOR_CODE[0]
  page = Page.model_validate_json(AMIS_EDITOR_CODE[1])
