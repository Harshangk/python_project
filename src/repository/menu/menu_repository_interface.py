from abc import ABC, abstractmethod


class MenuRepositoryInterface(ABC):

    @abstractmethod
    async def get_menu(
        self,
        role_id: int,
    ):
        pass
