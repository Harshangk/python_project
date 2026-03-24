from typing import List

from repository.menu.menu_repository_interface import MenuRepositoryInterface
from schema.menu.menu import MenuResponse
from services.menu.menu_service_interface import MenuServiceInterface


class MenuService(MenuServiceInterface):
    def __init__(self, menu_repository: MenuRepositoryInterface) -> None:
        self.menu_repository = menu_repository

    async def get_menu(
        self,
        role_id: int,
    ) -> List[MenuResponse]:
        rows = await self.menu_repository.get_menu(role_id)
        menu_map = {}
        root_menus = []

        # Single pass: create objects
        for row in rows:
            menu = MenuResponse(**row)
            menu.children = []
            menu_map[row["id"]] = menu

        # Second pass: attach to parent (required)
        for row in rows:
            parent_id = row["parent_id"]
            menu = menu_map[row["id"]]

            if parent_id is None:
                root_menus.append(menu)
            else:
                parent = menu_map.get(parent_id)
                if parent:
                    parent.children.append(menu)

        return root_menus
