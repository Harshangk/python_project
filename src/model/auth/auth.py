from pydantic.dataclasses import dataclass


@dataclass
class Login:
    user_name: str
    password: str
