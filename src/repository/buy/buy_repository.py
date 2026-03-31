from typing import Any, Mapping, Sequence
from datetime import datetime

from sqlalchemy import asc, desc, func, insert, or_, select, update, cast, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.schema_types import BuyStatus
from app import constant
from auth.exceptions import CreationError
from model.buy.buy import BuyLead as BuyLeadModel
from orm.buy.buy import tblbuylead, tblbuylead_address
from orm.common.common import mstmake, mstmodel, mstbroker
from repository.buy.buy_repository_interface import BuyRepositoryInterface

LEAD_SEARCHABLE_COLUMNS = {
    "branch": tblbuylead.c.branch,
    "mobile": tblbuylead.c.mobile,
    "source": tblbuylead.c.source,
    "mode": tblbuylead.c.mode,
    "broker_name": tblbuylead.c.broker_name,
    "customer_name": tblbuylead.c.customer_name,
    "make": mstmake.c.make,
    "model": mstmodel.c.model,
    "fuel_type": tblbuylead.c.fuel_type,
    "year": tblbuylead.c.year,
    "kms": tblbuylead.c.kms,
    "owner": tblbuylead.c.owner,
    "status": tblbuylead.c.status,
    "telecaller": tblbuylead.c.telecaller,
    "executive": tblbuylead.c.executive,
}

LEAD_SORTABLE_COLUMNS = {
    "id": tblbuylead.c.id,
    "mobile": tblbuylead.c.mobile,
    "source": tblbuylead.c.source,
    "mode": tblbuylead.c.mode,
    "make": mstmake.c.make,
    "model": mstmodel.c.model,
}

LEAD_COLUMNS = [
    tblbuylead.c.id,
    tblbuylead.c.branch,
    tblbuylead.c.mobile,
    tblbuylead.c.alternate_mobile,
    tblbuylead.c.source,
    tblbuylead.c.mode,
    tblbuylead.c.broker_name,
    tblbuylead.c.customer_name,
    tblbuylead.c.make_id,
    tblbuylead.c.model_id,
    tblbuylead.c.variant,
    tblbuylead.c.color,
    tblbuylead.c.fuel_type,
    tblbuylead.c.year,
    tblbuylead.c.kms,
    tblbuylead.c.owner,
    tblbuylead.c.client_offer,
    tblbuylead.c.our_offer,
    tblbuylead.c.status,
    tblbuylead.c.telecaller,
    tblbuylead.c.executive,
    tblbuylead.c.remarks,
    tblbuylead.c.allocated_at,
    tblbuylead.c.allocated_by,
    tblbuylead.c.created_at,
    tblbuylead.c.created_by,
    mstmake.c.make,
    mstmodel.c.model,
]


class BuyRepository(BuyRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    async def create_lead(self, lead: BuyLeadModel, created_by: str) -> int:
        try:
            if lead.telecaller is None and lead.executive is None:
                status = BuyStatus.NotAllocated.value
                allocated_by = None
                allocated_at = None
            else:
                status = BuyStatus.Allocated.value
                allocated_at = func.now()
                allocated_by = created_by
            stmt = (
                insert(tblbuylead)
                .values(
                    branch=lead.branch,
                    mobile=lead.mobile,
                    alternate_mobile=lead.alternate_mobile,
                    source=lead.source,
                    mode=lead.mode.value,
                    broker_name=lead.broker_name,
                    customer_name=lead.customer_name,
                    make_id=lead.make_id,
                    model_id=lead.model_id,
                    variant=lead.variant,
                    color=lead.color.value if lead.color else None,
                    fuel_type=lead.fuel_type.value,
                    year=str(lead.year),
                    kms=lead.kms,
                    owner=lead.owner,
                    client_offer=lead.client_offer,
                    our_offer=lead.our_offer,
                    status=status,
                    telecaller=lead.telecaller,
                    executive=lead.executive,
                    remarks=lead.remarks,
                    allocated_at=allocated_at,
                    allocated_by=allocated_by,
                    created_by=created_by,
                )
                .returning(tblbuylead.c.id)
            )
            result = await self.session.execute(stmt)
            buylead_id = result.scalar_one() 

            if lead.lead_address:
                stmt = (
                    insert(tblbuylead_address)
                    .values(
                        buylead_id=buylead_id,
                        address=lead.lead_address.address,
                        state=lead.lead_address.state,
                        city=lead.lead_address.city,
                        area=lead.lead_address.area,
                        pincode=lead.lead_address.pincode,
                    )
                )
                await self.session.execute(stmt)

            await self.session.commit()
            return buylead_id
        except IntegrityError:
            await self.session.rollback()
            raise CreationError(constant.FAILED)

    def _base_lead_query(self):
        return (
            select(*LEAD_COLUMNS)
            .join(mstmake, tblbuylead.c.make_id == mstmake.c.id)
            .join(mstmodel, tblbuylead.c.model_id == mstmodel.c.id)
            .where(tblbuylead.c.is_active)
        )

    def _apply_search(self, stmt, search: str | None):
        if search:
            filters = []

            for col in LEAD_SEARCHABLE_COLUMNS.values():
                if col is None:
                    continue

                if hasattr(col.type, "python_type") and col.type.python_type is str:
                    filters.append(col.ilike(f"%{search}%"))

                else:
                    filters.append(cast(col, String).ilike(f"%{search}%"))

            stmt = stmt.where(or_(*filters))

        return stmt

    def _apply_sort(self, stmt, sort_by: str | None, sort_order: str | None):
        sort_column = LEAD_SORTABLE_COLUMNS.get(sort_by, tblbuylead.c.id)

        if (sort_order or "").lower() == "asc":
            return stmt.order_by(asc(sort_column))
        return stmt.order_by(desc(sort_column))

    async def get_lead(
        self,
        cursor: int | None,
        limit: int,
        search: str | None = None,
        buy_status: BuyStatus | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = self._base_lead_query()
        stmt = self._apply_search(stmt, search)

        if buy_status:
            stmt = stmt.where(tblbuylead.c.status == buy_status)
        if cursor:
            if sort_order == "desc":
                stmt = stmt.where(tblbuylead.c.id < cursor)
            else:
                stmt = stmt.where(tblbuylead.c.id > cursor)

        stmt = self._apply_sort(stmt, sort_by, sort_order)
        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return result.mappings().all()

    async def get_total_lead(self, search: str | None = None, buy_status: BuyStatus | None = None) -> int:
        stmt = (
            select(func.count())
            .select_from(tblbuylead)
            .join(mstmake, tblbuylead.c.make_id == mstmake.c.id)
            .join(mstmodel, tblbuylead.c.model_id == mstmodel.c.id)
            .where(tblbuylead.c.is_active)
        )
        
        stmt = self._apply_search(stmt, search)
        if buy_status:
            stmt = stmt.where(tblbuylead.c.status == buy_status)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_lead_export(
        self,
        search: str | None = None,
        buy_status: BuyStatus | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ):
        stmt = self._base_lead_query()
        stmt = self._apply_search(stmt, search)
        if buy_status:
            stmt = stmt.where(tblbuylead.c.status == buy_status)
        stmt = self._apply_sort(stmt, sort_by, sort_order)

        stmt = stmt.execution_options(stream_results=True)

        stream = await self.session.stream(stmt)
        async for row in stream:
            yield dict(row._mapping)


    async def get_lead_by_id(
        self,
        lead_id: int,
    ) -> BuyLeadModel:
        stmt = self._base_lead_query()
        stmt = stmt.where(
            tblbuylead.c.id == lead_id,
            tblbuylead.c.is_active.is_(True),
            tblbuylead.c.is_deleted.is_(False)
        )
        result = await self.session.execute(stmt)
        return result.mappings().one_or_none()


    async def remove_lead(self, lead_id: int, created_by: str) -> bool:
        stmt = (
            update(tblbuylead)
            .where(
                tblbuylead.c.id == lead_id,
                tblbuylead.c.is_active.is_(True),
                tblbuylead.c.is_deleted.is_(False)
            )
            .values(
                modified_by=created_by,
                modified_at=datetime.now,
                is_active=False,
                is_deleted=True
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0
