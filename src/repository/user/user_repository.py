from typing import Any, Mapping, Sequence

from sqlalchemy import asc, desc, func, insert, or_, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import constant
from app.core.security import pwd_context
from auth.exceptions import CreationError
from model.user.user import User as UserModel
from orm.user.user import mstlogin, mstrole
from repository.user.user_repository_interface import UserRepositoryInterface

USER_SEARCHABLE_COLUMNS = {
    "user_name": mstlogin.c.user_name,
    "role": mstrole.c.role,
}

USER_SORTABLE_COLUMNS = {
    "id": mstlogin.c.id,
    "user_name": mstlogin.c.user_name,
    "role": mstrole.c.role,
}


class UserRepository(UserRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    async def create_user(self, user: UserModel, created_by: str) -> int:
        try:
            stmt = insert(mstlogin).values(
                role_id=user.role,
                user_name=user.user_name,
                password=pwd_context.hash(user.password),
                created_by=created_by,
            )

            result = await self.session.execute(stmt)
            await self.session.commit()

            return result.inserted_primary_key[0]
        except IntegrityError:
            raise CreationError(constant.FAILED)

    async def get_user(
        self,
        cursor: int | None,
        limit: int,
        role_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = select(
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
        ).join(mstrole, mstlogin.c.role_id == mstrole.c.id)

        if role_id is not None:
            stmt = stmt.where(mstlogin.c.role_id == role_id)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in USER_SEARCHABLE_COLUMNS.values()
            ]
            stmt = stmt.where(or_(*search_filters))

        if cursor:
            stmt = stmt.where(mstlogin.c.id > cursor)

        sort_column = USER_SORTABLE_COLUMNS.get(sort_by, mstlogin.c.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return rows

    async def get_total_user(
        self, role_id: int | None = None, search: str | None = None
    ) -> int:
        query = select(func.count()).select_from(
            mstlogin.join(mstrole, mstlogin.c.role_id == mstrole.c.id)
        )

        if role_id is not None:
            query = query.where(mstlogin.c.role_id == role_id)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in USER_SEARCHABLE_COLUMNS.values()
            ]
            query = query.where(or_(*search_filters))

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_user_export(
        self,
        role_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ):
        stmt = select(
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
        ).join(mstrole, mstlogin.c.role_id == mstrole.c.id)

        if role_id is not None:
            stmt = stmt.where(mstlogin.c.role_id == role_id)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in USER_SEARCHABLE_COLUMNS.values()
            ]
            stmt = stmt.where(or_(*search_filters))

        sort_column = USER_SORTABLE_COLUMNS.get(sort_by, mstlogin.c.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        stmt = stmt.execution_options(stream_results=True)
        stream = await self.session.stream(stmt)
        async for row in stream:
            yield dict(row._mapping)

    async def get_user_by_id(self, user_id: int):
        stmt = (
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
            .where(mstlogin.c.id == user_id, ~mstlogin.c.is_lock)
        )

        result = await self.session.execute(stmt)
        user = result.mappings().one_or_none()
        return user

    async def lock_user(self, user_id: int) -> bool:
        stmt = (
            update(mstlogin)
            .where(mstlogin.c.id == user_id, ~mstlogin.c.is_lock)
            .values(is_lock=True)
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0
