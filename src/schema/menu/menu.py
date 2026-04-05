from typing import List, Optional

from common.schema_types import CamelBaseModel


class MenuBase(CamelBaseModel):
    id: int
    menu_name: str
    menu_icon: Optional[str]
    menu_path: Optional[str]
    badge_count: Optional[int]


class MenuResponse(MenuBase):
    children: List["MenuResponse"] = []
