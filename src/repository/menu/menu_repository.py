from sqlalchemy import nullsfirst, select
from sqlalchemy.orm import Session

from orm.menu.menu import maprolemenu, mstmenu
from repository.menu.menu_repository_interface import MenuRepositoryInterface


class MenuRepository(MenuRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    async def get_menu(
        self,
        role_id: int,
    ):
        stmt = (
            select(
                mstmenu.c.id,
                mstmenu.c.menu_name,
                mstmenu.c.menu_icon,
                mstmenu.c.menu_path,
                mstmenu.c.parent_id,
                mstmenu.c.order_no,
                mstmenu.c.badge_count,
            )
            .join(maprolemenu, maprolemenu.c.menu_id == mstmenu.c.id)
            .where(
                maprolemenu.c.role_id == role_id,
                mstmenu.c.is_active,
                ~mstmenu.c.is_deleted,
            )
            .order_by(nullsfirst(mstmenu.c.parent_id), mstmenu.c.order_no)
        )

        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return rows
