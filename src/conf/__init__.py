from .base import CONF_DIR, ROOT_DIR, read_sql_conf, read_conf
from .amis_template import AMIS_EDITOR_CODE, AMIS_TEMPLATE, HEADERS

APP_CONF = read_conf('app')
SQL_CONF = read_sql_conf()
MAIN_CONF = read_conf('main')