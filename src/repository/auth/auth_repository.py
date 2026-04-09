from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from orm.user.user import mstlogin, mstrole
from repository.auth.auth_repository_interface import AuthRepositoryInterface


class AuthRepository(AuthRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def _base_user_query(self, username: str):
        return (
            select(
                mstlogin.c.id,
                mstlogin.c.user_name,
                mstlogin.c.password,
                mstlogin.c.role_id,
                mstrole.c.role,
                mstlogin.c.last_login,
                mstlogin.c.login_at,
                mstlogin.c.created_at,
                mstlogin.c.created_by,
                mstlogin.c.expiry_at,
                mstlogin.c.is_lock,
                mstlogin.c.is_active,
            )
            .join(mstrole, mstlogin.c.role_id == mstrole.c.id)
            .where(
                (mstlogin.c.user_name == username)
                & (mstlogin.c.is_active)
                & (~mstlogin.c.is_deleted)
                & (~mstlogin.c.is_lock)
            )
        )

    async def login(self, username: str):
        result = await self.session.execute(self._base_user_query(username))
        return result.one_or_none()

    async def last_login(self, username: str):
        await self.session.execute(
            update(mstlogin)
            .where(mstlogin.c.user_name == username)
            .values(last_login=mstlogin.c.login_at, login_at=func.now())
        )
        await self.session.commit()
        result = await self.session.execute(self._base_user_query(username))
        return result.one_or_none()
