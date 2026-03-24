from pydantic.dataclasses import dataclass


@dataclass
class Menu:
    menu_name: str
    menu_icon: str
    menu_path: str
    parent_id: int
    order_no: int
    badge_count: int


@dataclass
class RoleMenu:
    role_id: int
    menu_id: int
