from abc import ABC, abstractmethod


class AuthRepositoryInterface(ABC):

    @abstractmethod
    async def login(self, user_name: str):
        pass

    @abstractmethod
    async def last_login(self, user_name: str):
        pass
