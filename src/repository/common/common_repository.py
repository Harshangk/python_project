from typing import Any, Mapping, Sequence

from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.orm import Session

from orm.common.common import (
    mstbranch,
    mstbroker,
    mstcity,
    mstmake,
    mstmodel,
    mstsource,
    mststate,
    mstyear,
)
from repository.common.common_repository_interface import CommonRepositoryInterface

MAKE_SEARCHABLE_COLUMNS = {
    "make": mstmake.c.make,
    "is_premium": mstmake.c.is_premium,
}

MAKE_SORTABLE_COLUMNS = {
    "id": mstmake.c.id,
    "make": mstmake.c.make,
    "is_premium": mstmake.c.is_premium,
}

MODEL_SEARCHABLE_COLUMNS = {
    "make_id": mstmodel.c.make_id,
    "model": mstmodel.c.model,
}

MODEL_SORTABLE_COLUMNS = {
    "id": mstmodel.c.id,
    "make_id": mstmodel.c.make_id,
    "model": mstmodel.c.model,
}

BRANCH_SEARCHABLE_COLUMNS = {
    "branch": mstbranch.c.branch,
}

BRANCH_SORTABLE_COLUMNS = {
    "id": mstbranch.c.id,
    "branch": mstbranch.c.branch,
}

SOURCE_SEARCHABLE_COLUMNS = {
    "source": mstsource.c.source,
}

SOURCE_SORTABLE_COLUMNS = {
    "id": mstsource.c.id,
    "source": mstsource.c.source,
}

YEAR_SEARCHABLE_COLUMNS = {
    "year": mstyear.c.year,
}

BROKER_SEARCHABLE_COLUMNS = {
    "broker": mstbroker.c.broker,
}

BROKER_SORTABLE_COLUMNS = {
    "id": mstbroker.c.id,
    "broker": mstbroker.c.broker,
}

STATE_SEARCHABLE_COLUMNS = {
    "state": mststate.c.state,
}

STATE_SORTABLE_COLUMNS = {
    "id": mststate.c.id,
    "state": mststate.c.state,
}

CITY_SEARCHABLE_COLUMNS = {
    "city_id": mstcity.c.state_id,
    "city": mstcity.c.city,
}

CITY_SORTABLE_COLUMNS = {
    "id": mstcity.c.id,
    "state_id": mstcity.c.state_id,
    "city": mstcity.c.city,
}


class CommonRepository(CommonRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    async def get_source(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = select(
            mstsource.c.id,
            mstsource.c.source,
            mstsource.c.created_at,
            mstsource.c.created_by,
        ).where(mstsource.c.is_active)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in SOURCE_SEARCHABLE_COLUMNS.values()
            ]
            stmt = stmt.where(or_(*search_filters))

        if cursor:
            stmt = stmt.where(mstsource.c.id > cursor)

        sort_column = SOURCE_SORTABLE_COLUMNS.get(sort_by, mstsource.c.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return rows

    async def get_total_source(self, search: str | None = None) -> int:
        query = select(func.count()).select_from(mstsource).where(mstsource.c.is_active)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in SOURCE_SEARCHABLE_COLUMNS.values()
            ]
            query = query.where(or_(*search_filters))

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_make(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = select(
            mstmake.c.id,
            mstmake.c.make,
            mstmake.c.is_premium,
            mstmake.c.created_at,
            mstmake.c.created_by,
        ).where(mstmake.c.is_active)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in MAKE_SEARCHABLE_COLUMNS.values()
            ]
            stmt = stmt.where(or_(*search_filters))

        if cursor:
            stmt = stmt.where(mstmake.c.id > cursor)

        sort_column = MAKE_SORTABLE_COLUMNS.get(sort_by, mstmake.c.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return rows

    async def get_total_make(self, search: str | None = None) -> int:
        query = select(func.count()).select_from(mstmake).where(mstmake.c.is_active)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in MAKE_SEARCHABLE_COLUMNS.values()
            ]
            query = query.where(or_(*search_filters))

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_model(
        self,
        cursor: int | None,
        limit: int,
        make_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = (
            select(
                mstmodel.c.id,
                mstmodel.c.make_id,
                mstmodel.c.model,
                mstmodel.c.created_at,
                mstmodel.c.created_by,
                mstmake.c.make,
            )
            .join(mstmake, mstmodel.c.make_id == mstmake.c.id)
            .where(mstmodel.c.is_active)
        )

        if make_id is not None:
            stmt = stmt.where(mstmodel.c.make_id == make_id)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in MODEL_SEARCHABLE_COLUMNS.values()
            ]
            stmt = stmt.where(or_(*search_filters))

        if cursor:
            stmt = stmt.where(mstmodel.c.id > cursor)

        sort_column = MODEL_SORTABLE_COLUMNS.get(sort_by, mstmodel.c.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return rows

    async def get_total_model(
        self, make_id: int | None = None, search: str | None = None
    ) -> int:
        query = (
            select(func.count())
            .select_from(mstmodel.join(mstmake, mstmodel.c.make_id == mstmake.c.id))
            .where(mstmodel.c.is_active)
        )

        if make_id is not None:
            query = query.where(mstmodel.c.make_id == make_id)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in MODEL_SEARCHABLE_COLUMNS.values()
            ]
            query = query.where(or_(*search_filters))

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_branch(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = select(
            mstbranch.c.id,
            mstbranch.c.branch,
            mstbranch.c.created_at,
            mstbranch.c.created_by,
        ).where(mstbranch.c.is_active)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in BRANCH_SEARCHABLE_COLUMNS.values()
            ]
            stmt = stmt.where(or_(*search_filters))

        if cursor:
            stmt = stmt.where(mstbranch.c.id > cursor)

        sort_column = BRANCH_SORTABLE_COLUMNS.get(sort_by, mstbranch.c.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return rows

    async def get_total_branch(self, search: str | None = None) -> int:
        query = select(func.count()).select_from(mstbranch).where(mstbranch.c.is_active)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in BRANCH_SEARCHABLE_COLUMNS.values()
            ]
            query = query.where(or_(*search_filters))

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_broker(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = select(
            mstbroker.c.id,
            mstbroker.c.broker,
            mstbroker.c.created_at,
            mstbroker.c.created_by,
        ).where(mstbroker.c.is_active)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in BROKER_SEARCHABLE_COLUMNS.values()
            ]
            stmt = stmt.where(or_(*search_filters))

        if cursor:
            stmt = stmt.where(mstbroker.c.id > cursor)

        sort_column = BROKER_SORTABLE_COLUMNS.get(sort_by, mstbroker.c.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)

        rows = result.mappings().all()
        return rows

    async def get_total_broker(self, search: str | None = None) -> int:
        query = select(func.count()).select_from(mstbroker).where(mstbroker.c.is_active)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in BROKER_SEARCHABLE_COLUMNS.values()
            ]
            query = query.where(or_(*search_filters))

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_year(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = select(
            mstyear.c.year,
        )

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in YEAR_SEARCHABLE_COLUMNS.values()
            ]
            stmt = stmt.where(or_(*search_filters))

        if cursor:
            stmt = stmt.where(mstbroker.c.id > cursor)

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return rows

    async def get_total_year(self, search: str | None = None) -> int:
        query = select(func.count()).select_from(mstyear)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in YEAR_SEARCHABLE_COLUMNS.values()
            ]
            query = query.where(or_(*search_filters))

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_state(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = select(
            mststate.c.id,
            mststate.c.state,
            mststate.c.created_at,
            mststate.c.created_by,
        ).where(mststate.c.is_active)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in STATE_SEARCHABLE_COLUMNS.values()
            ]
            stmt = stmt.where(or_(*search_filters))

        if cursor:
            stmt = stmt.where(mststate.c.id > cursor)

        sort_column = STATE_SORTABLE_COLUMNS.get(sort_by, mststate.c.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return rows

    async def get_total_state(self, search: str | None = None) -> int:
        query = select(func.count()).select_from(mststate).where(mststate.c.is_active)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in STATE_SEARCHABLE_COLUMNS.values()
            ]
            query = query.where(or_(*search_filters))

        result = await self.session.execute(query)
        return result.scalar_one()

    async def get_city(
        self,
        cursor: int | None,
        limit: int,
        state_id: int | None = None,
        search: str | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = (
            select(
                mstcity.c.id,
                mstcity.c.state_id,
                mstcity.c.city,
                mstcity.c.created_at,
                mstcity.c.created_by,
                mststate.c.state,
            )
            .join(mststate, mstcity.c.state_id == mststate.c.id)
            .where(mstcity.c.is_active)
        )

        if state_id is not None:
            stmt = stmt.where(mstcity.c.state_id == state_id)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in CITY_SEARCHABLE_COLUMNS.values()
            ]
            stmt = stmt.where(or_(*search_filters))

        if cursor:
            stmt = stmt.where(mstcity.c.id > cursor)

        sort_column = CITY_SORTABLE_COLUMNS.get(sort_by, mstcity.c.id)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_column))
        else:
            stmt = stmt.order_by(desc(sort_column))

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        rows = result.mappings().all()
        return rows

    async def get_total_city(
        self, state_id: int | None = None, search: str | None = None
    ) -> int:
        query = (
            select(func.count())
            .select_from(mstcity.join(mststate, mstcity.c.state_id == mststate.c.id))
            .where(mstcity.c.is_active)
        )

        if state_id is not None:
            query = query.where(mstcity.c.state_id == state_id)

        if search:
            search_filters = [
                col.ilike(f"%{search}%") for col in CITY_SEARCHABLE_COLUMNS.values()
            ]
            query = query.where(or_(*search_filters))

        result = await self.session.execute(query)
        return result.scalar_one()
