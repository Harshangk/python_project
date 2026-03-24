from abc import ABC, abstractmethod


class MenuServiceInterface(ABC):

    @abstractmethod
    async def get_menu(
        self,
        role_id: int,
    ):
        pass
