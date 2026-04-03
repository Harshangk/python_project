"""Import all the models, so that Base has them before being imported by Alembic"""

from common.db import Base

from orm.buy import buy as buy_orm
from orm.common import common as common_orm
from orm.menu import menu as menu_orm
from orm.user import user as user_orm