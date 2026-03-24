from abc import ABC, abstractmethod


class AuthServiceInterface(ABC):

    @abstractmethod
    async def login(self, user_name: str, password: str):
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str):
        pass

    @abstractmethod
    async def logout(self, token: str):
        pass
