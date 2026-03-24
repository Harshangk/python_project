from pydantic.dataclasses import dataclass


@dataclass
class User:
    role: int
    user_name: str
    password: str
    created_by: str | None = None
