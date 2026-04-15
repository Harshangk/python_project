from typing import Any, Mapping, Sequence
from uuid import UUID

from sqlalchemy import String, asc, cast, desc, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import constant
from auth.exceptions import AllocationError, CreationError, NotFound
from common.schema_types import BuyDisposition, BuyStage, BuyStatus, FileStatus
from model.buy.buy import AllocateLeadsRequest
from model.buy.buy import BuyLead as BuyLeadModel
from model.buy.buy import BuyLeadFile, BuyLeadFollowup, BuyLeadFollowupDetail
from orm.buy.buy import (
    tblbuylead,
    tblbuylead_address,
    tblbuylead_file,
    tblbuylead_followup,
)
from orm.common.common import mstmake, mstmodel
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
    tblbuylead_address.c.address,
    tblbuylead_address.c.state,
    tblbuylead_address.c.city,
    tblbuylead_address.c.area,
    tblbuylead_address.c.pincode,
]

FOLLOWUP_LEAD_SEARCHABLE_COLUMNS = {
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
    "stage": tblbuylead_followup.c.stage,
    "disposition": tblbuylead_followup.c.disposition,
}

FOLLOWUP_LEAD_COLUMNS = [
    tblbuylead.c.id,
    tblbuylead.c.status,
    tblbuylead.c.mobile,
    tblbuylead.c.alternate_mobile,
    tblbuylead.c.customer_name,
    tblbuylead_followup.c.stage,
    tblbuylead_followup.c.disposition,
    tblbuylead_followup.c.calldate,
    tblbuylead_followup.c.preferred_time,
    tblbuylead_followup.c.notes,
    tblbuylead.c.branch,
    tblbuylead.c.source,
    tblbuylead.c.mode,
    tblbuylead.c.broker_name,
    tblbuylead.c.make_id,
    tblbuylead.c.model_id,
    mstmake.c.make,
    mstmodel.c.model,
    tblbuylead.c.variant,
    tblbuylead.c.color,
    tblbuylead.c.fuel_type,
    tblbuylead.c.year,
    tblbuylead.c.kms,
    tblbuylead.c.owner,
    tblbuylead.c.client_offer,
    tblbuylead.c.our_offer,
    tblbuylead.c.telecaller,
    tblbuylead.c.executive,
    tblbuylead.c.allocated_at,
    tblbuylead.c.allocated_by,
    tblbuylead.c.created_at,
    tblbuylead.c.created_by,
    tblbuylead.c.remarks,
    tblbuylead_address.c.address,
    tblbuylead_address.c.state,
    tblbuylead_address.c.city,
    tblbuylead_address.c.area,
    tblbuylead_address.c.pincode,
    tblbuylead_followup.c.created_at.label("followupCreatedAt"),
    tblbuylead_followup.c.created_by.label("followupCreatedBy"),
]

IMPORT_LEAD_COLUMNS = [
    tblbuylead_file.c.id,
    tblbuylead_file.c.s3_key,
    tblbuylead_file.c.file_status,
    tblbuylead_file.c.file_uuid,
    tblbuylead_file.c.processed_records,
    tblbuylead_file.c.error_records,
    tblbuylead_file.c.error_s3_key,
    tblbuylead_file.c.created_at,
    tblbuylead_file.c.created_by,
]

IMPORT_LEAD_SEARCHABLE_COLUMNS = {
    "s3_key": tblbuylead.c.branch,
    "file_status": tblbuylead.c.mobile,
    "file_uuid": tblbuylead.c.source,
    "error_s3_key": tblbuylead_file.c.error_s3_key,
}


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
                stmt = insert(tblbuylead_address).values(
                    buylead_id=buylead_id,
                    address=lead.lead_address.address,
                    state=lead.lead_address.state,
                    city=lead.lead_address.city,
                    area=lead.lead_address.area,
                    pincode=lead.lead_address.pincode,
                )
                await self.session.execute(stmt)

            if status == BuyStatus.Allocated.value:
                stmt = insert(tblbuylead_followup).values(
                    buylead_id=buylead_id,
                    stage=BuyStage.Fresh.value,
                    disposition=BuyDisposition.Fresh.value,
                    calldate=func.now(),
                    notes=BuyStage.Fresh.value,
                    created_at=func.now(),
                    created_by=created_by,
                )
                await self.session.execute(stmt)

            await self.session.commit()
            return buylead_id
        except IntegrityError:
            await self.session.rollback()
            raise CreationError(constant.FAILED)

    async def update_lead(
        self, lead_id: int, lead: BuyLeadModel, created_by: str
    ) -> int:
        try:
            existing_stmt = select(
                tblbuylead.c.id,
            ).where(
                tblbuylead.c.id == lead_id,
                tblbuylead.c.is_active.is_(True),
                tblbuylead.c.is_deleted.is_(False),
            )

            result = await self.session.execute(existing_stmt)
            existing = result.fetchone()

            if not existing:
                raise NotFound(constant.NOTFOUND)

            stmt = (
                update(tblbuylead)
                .where(
                    tblbuylead.c.id == lead_id,
                    tblbuylead.c.is_active.is_(True),
                    tblbuylead.c.is_deleted.is_(False),
                )
                .values(
                    branch=lead.branch,
                    alternate_mobile=lead.alternate_mobile,
                    source=lead.source,
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
                    remarks=lead.remarks,
                    modified_by=created_by,
                    modified_at=func.now(),
                )
            )
            await self.session.execute(stmt)

            if lead.lead_address:
                stmt = insert(tblbuylead_address).values(
                    buylead_id=lead_id,
                    address=lead.lead_address.address,
                    state=lead.lead_address.state,
                    city=lead.lead_address.city,
                    area=lead.lead_address.area,
                    pincode=lead.lead_address.pincode,
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=[tblbuylead_address.c.buylead_id],
                    set_=dict(
                        address=lead.lead_address.address,
                        state=lead.lead_address.state,
                        city=lead.lead_address.city,
                        area=lead.lead_address.area,
                        pincode=lead.lead_address.pincode,
                    ),
                )
                await self.session.execute(stmt)

            await self.session.commit()
            return lead_id
        except IntegrityError:
            await self.session.rollback()
            raise CreationError(constant.FAILED)

    def _base_lead_query(self):
        return (
            select(*LEAD_COLUMNS)
            .join(mstmake, tblbuylead.c.make_id == mstmake.c.id)
            .join(mstmodel, tblbuylead.c.model_id == mstmodel.c.id)
            .outerjoin(
                tblbuylead_address, tblbuylead.c.id == tblbuylead_address.c.buylead_id
            )
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

    async def get_total_lead(
        self, search: str | None = None, buy_status: BuyStatus | None = None
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(tblbuylead)
            .join(mstmake, tblbuylead.c.make_id == mstmake.c.id)
            .join(mstmodel, tblbuylead.c.model_id == mstmodel.c.id)
            .outerjoin(
                tblbuylead_address, tblbuylead.c.id == tblbuylead_address.c.buylead_id
            )
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
            tblbuylead.c.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.mappings().one_or_none()

    async def remove_lead(self, lead_id: int, created_by: str) -> bool:
        stmt = (
            update(tblbuylead)
            .where(
                tblbuylead.c.id == lead_id,
                tblbuylead.c.is_active.is_(True),
                tblbuylead.c.is_deleted.is_(False),
            )
            .values(
                modified_by=created_by,
                modified_at=func.now(),
                is_active=False,
                is_deleted=True,
            )
        )

        result = await self.session.execute(stmt)
        await self.session.commit()

        return result.rowcount > 0

    async def allocate_leads(
        self, allocate: AllocateLeadsRequest, created_by: str
    ) -> int:
        try:
            update_data = {
                "allocated_at": func.now(),
                "allocated_by": created_by,
                "status": BuyStatus.Allocated.value,
            }

            if allocate.telecaller:
                update_data["telecaller"] = allocate.telecaller

            if allocate.executive:
                update_data["executive"] = allocate.executive

            update_stmt = (
                update(tblbuylead)
                .where(
                    tblbuylead.c.id.in_(allocate.lead_ids),
                    tblbuylead.c.is_active.is_(True),
                    tblbuylead.c.is_deleted.is_(False),
                    tblbuylead.c.status == BuyStatus.NotAllocated.value,
                )
                .values(**update_data)
            )
            result = await self.session.execute(update_stmt)

            followup_data = [
                {
                    "buylead_id": lead_id,
                    "stage": BuyStage.Fresh.value,
                    "disposition": BuyDisposition.Fresh.value,
                    "calldate": func.now(),
                    "notes": BuyStage.Fresh.value,
                }
                for lead_id in allocate.lead_ids
            ]

            insert_stmt = insert(tblbuylead_followup).values(followup_data)
            await self.session.execute(insert_stmt)

            await self.session.commit()
            return result.rowcount
        except IntegrityError:
            await self.session.rollback()
            raise AllocationError(constant.FAILED)

    async def reallocate_leads(
        self, reallocate: AllocateLeadsRequest, created_by: str
    ) -> int:
        try:
            update_data = {}
            update_data["telecaller"] = reallocate.telecaller
            update_data["executive"] = reallocate.executive

            stmt = (
                update(tblbuylead)
                .where(
                    tblbuylead.c.id.in_(reallocate.lead_ids),
                    tblbuylead.c.is_active.is_(True),
                    tblbuylead.c.is_deleted.is_(False),
                    tblbuylead.c.status == BuyStatus.Allocated.value,
                )
                .values(**update_data)
            )
            result = await self.session.execute(stmt)
            await self.session.commit()
            return result.rowcount
        except IntegrityError:
            await self.session.rollback()
            raise AllocationError(constant.FAILED)

    async def create_lead_followup(
        self, lead_id: int, lead: BuyLeadFollowup, created_by: str
    ) -> int:
        try:
            stage_to_status_map = {
                BuyStage.Appointment.value: BuyStatus.Appointment.value,
                BuyStage.Lost.value: BuyStatus.Lost.value,
                BuyStage.DND.value: BuyStatus.DND.value,
            }

            status = stage_to_status_map.get(
                lead.lead_followup.stage, BuyStatus.Allocated.value
            )

            existing_stmt = select(
                tblbuylead.c.id,
            ).where(
                tblbuylead.c.id == lead_id,
                tblbuylead.c.is_active.is_(True),
                tblbuylead.c.is_deleted.is_(False),
                or_(
                    tblbuylead.c.status == BuyStatus.Allocated.value,
                    tblbuylead.c.status == BuyStatus.Appointment.value,
                ),
            )

            result = await self.session.execute(existing_stmt)
            existing = result.fetchone()

            if not existing:
                raise NotFound(constant.NOTFOUND)

            stmt = (
                update(tblbuylead)
                .where(
                    tblbuylead.c.id == lead_id,
                    tblbuylead.c.is_active.is_(True),
                    tblbuylead.c.is_deleted.is_(False),
                    or_(
                        tblbuylead.c.status == BuyStatus.Allocated.value,
                        tblbuylead.c.status == BuyStatus.Appointment.value,
                    ),
                )
                .values(
                    branch=lead.branch,
                    customer_name=lead.customer_name,
                    alternate_mobile=lead.alternate_mobile,
                    mode=lead.mode,
                    source=lead.source,
                    broker_name=lead.broker_name,
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
                    telecaller=lead.telecaller,
                    executive=lead.executive,
                    status=status,
                    modified_by=created_by,
                    modified_at=func.now(),
                )
            )
            await self.session.execute(stmt)

            if lead.lead_address:
                stmt = insert(tblbuylead_address).values(
                    buylead_id=lead_id,
                    address=lead.lead_address.address,
                    state=lead.lead_address.state,
                    city=lead.lead_address.city,
                    area=lead.lead_address.area,
                    pincode=lead.lead_address.pincode,
                )
                stmt = stmt.on_conflict_do_update(
                    index_elements=[tblbuylead_address.c.buylead_id],
                    set_=dict(
                        address=lead.lead_address.address,
                        state=lead.lead_address.state,
                        city=lead.lead_address.city,
                        area=lead.lead_address.area,
                        pincode=lead.lead_address.pincode,
                    ),
                )
                await self.session.execute(stmt)

            stmt = (
                update(tblbuylead_followup)
                .where(tblbuylead_followup.c.buylead_id == lead_id)
                .values(
                    stage=lead.lead_followup.stage,
                    disposition=lead.lead_followup.disposition,
                    calldate=lead.lead_followup.calldate,
                    preferred_time=lead.lead_followup.preferred_time,
                    notes=lead.lead_followup.notes,
                    created_at=func.now(),
                    created_by=created_by,
                )
            )
            await self.session.execute(stmt)

            await self.session.commit()
            return lead_id
        except IntegrityError:
            await self.session.rollback()
            raise CreationError(constant.FAILED)

    def _base_followup_lead_query(self, created_by: str, role_id: int):
        stmt = (
            select(*FOLLOWUP_LEAD_COLUMNS)
            .join(mstmake, tblbuylead.c.make_id == mstmake.c.id)
            .join(mstmodel, tblbuylead.c.model_id == mstmodel.c.id)
            .join(
                tblbuylead_followup, tblbuylead.c.id == tblbuylead_followup.c.buylead_id
            )
            .outerjoin(
                tblbuylead_address, tblbuylead.c.id == tblbuylead_address.c.buylead_id
            )
            .where(
                tblbuylead.c.is_active,
                tblbuylead.c.status != BuyStatus.NotAllocated.value,
            )
        )
        if role_id != 1:
            stmt = stmt.where(
                or_(
                    tblbuylead.c.telecaller == created_by,
                    tblbuylead.c.executive == created_by,
                )
            )
        return stmt

    def _apply_followup_search(self, stmt, search: str | None):
        if search:
            filters = []

            for col in FOLLOWUP_LEAD_SEARCHABLE_COLUMNS.values():
                if col is None:
                    continue

                if hasattr(col.type, "python_type") and col.type.python_type is str:
                    filters.append(col.ilike(f"%{search}%"))

                else:
                    filters.append(cast(col, String).ilike(f"%{search}%"))

            stmt = stmt.where(or_(*filters))

        return stmt

    async def get_followup_lead(
        self,
        cursor: int | None,
        limit: int,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = self._base_followup_lead_query(created_by, role_id)

        stmt = self._apply_followup_search(stmt, search)

        if cursor:
            stmt = stmt.where(tblbuylead.c.id < cursor)

        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return result.mappings().all()

    async def get_total_followup_lead(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(tblbuylead)
            .join(mstmake, tblbuylead.c.make_id == mstmake.c.id)
            .join(mstmodel, tblbuylead.c.model_id == mstmodel.c.id)
            .join(
                tblbuylead_followup, tblbuylead.c.id == tblbuylead_followup.c.buylead_id
            )
            .where(tblbuylead.c.is_active)
        )
        if role_id != 1:
            stmt = stmt.where(
                or_(
                    tblbuylead.c.telecaller == created_by,
                    tblbuylead.c.executive == created_by,
                )
            )

        stmt = self._apply_followup_search(stmt, search)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_followup_lead_export(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ):
        stmt = self._base_followup_lead_query(created_by, role_id)
        stmt = self._apply_followup_search(stmt, search)
        stmt = stmt.execution_options(stream_results=True)

        stream = await self.session.stream(stmt)
        async for row in stream:
            yield dict(row._mapping)

    async def get_followup_lead_by_id(
        self,
        lead_id: int,
        created_by: str,
        role_id: int,
    ) -> BuyLeadFollowupDetail:
        stmt = self._base_followup_lead_query(created_by=created_by, role_id=role_id)
        stmt = stmt.where(tblbuylead.c.id == lead_id)
        result = await self.session.execute(stmt)
        return result.mappings().one_or_none()

    def _base_import_lead_query(self, created_by: str, role_id: int):
        stmt = select(*IMPORT_LEAD_COLUMNS)
        if role_id != 1:
            stmt = stmt.where(or_(tblbuylead_file.c.created_by == created_by))
        return stmt

    def _apply_import_search(self, stmt, search: str | None):
        if search:
            filters = []

            for col in IMPORT_LEAD_SEARCHABLE_COLUMNS.values():
                if col is None:
                    continue

                if hasattr(col.type, "python_type") and col.type.python_type is str:
                    filters.append(col.ilike(f"%{search}%"))

                else:
                    filters.append(cast(col, String).ilike(f"%{search}%"))

            stmt = stmt.where(or_(*filters))

        return stmt

    async def create_lead_file_id(
        self,
        file_uuid: UUID,
        s3_key: str,
        status: FileStatus,
        created_by: str,
    ) -> int:
        try:
            stmt = (
                insert(tblbuylead_file)
                .values(
                    s3_key=s3_key,
                    file_status=status,
                    file_uuid=file_uuid,
                    processed_records=0,
                    error_records=0,
                    created_at=func.now(),
                    created_by=created_by,
                )
                .returning(tblbuylead_file.c.id)
            )
            result = await self.session.execute(stmt)
            buylead_file_id = result.scalar_one()

            await self.session.commit()
            return buylead_file_id
        except IntegrityError:
            await self.session.rollback()
            raise CreationError(constant.FAILED)

    async def patch_file_status(
        self,
        file_uuid: UUID,
        status: FileStatus,
        processed_records: int,
        error_records: int,
        error_file_key: str | None = None,
    ) -> int:
        try:
            existing_stmt = select(
                tblbuylead_file.c.id,
            ).where(tblbuylead_file.c.file_uuid == file_uuid)

            result = await self.session.execute(existing_stmt)
            existing = result.fetchone()

            if not existing:
                raise NotFound(constant.NOTFOUND)

            stmt = (
                update(tblbuylead_file)
                .where(tblbuylead_file.c.file_uuid == file_uuid)
                .values(
                    file_status=status,
                    processed_records=processed_records,
                    error_records=error_records,
                    error_s3_key=error_file_key,
                )
            )
            await self.session.execute(stmt)

            await self.session.commit()
            return file_uuid
        except IntegrityError:
            await self.session.rollback()
            raise CreationError(constant.FAILED)

    async def bulk_insert_lead(self, data):
        payload = [
            {k: v for k, v in vars(d).items() if not k.startswith("_")} for d in data
        ]
        await self.session.execute(insert(tblbuylead), payload)
        await self.session.commit()

    async def get_import_lead(
        self,
        cursor: int | None,
        limit: int,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = self._base_import_lead_query(created_by, role_id)

        stmt = self._apply_import_search(stmt, search)

        if cursor:
            stmt = stmt.where(tblbuylead_file.c.id < cursor)

        stmt = stmt.order_by(tblbuylead_file.c.id.desc())
        stmt = stmt.limit(limit)
        result = await self.session.execute(stmt)
        return result.mappings().all()

    async def get_total_import_lead(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ) -> int:
        stmt = select(func.count()).select_from(tblbuylead_file)
        if role_id != 1:
            stmt = stmt.where(or_(tblbuylead.c.created_by == created_by))

        stmt = self._apply_import_search(stmt, search)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_import_lead_export(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
    ):
        stmt = self._base_import_lead_query(created_by, role_id)
        stmt = self._apply_import_search(stmt, search)
        stmt = stmt.execution_options(stream_results=True)

        stream = await self.session.stream(stmt)
        async for row in stream:
            yield dict(row._mapping)

    async def get_import_lead_by_id(
        self,
        import_id: UUID,
        created_by: str,
        role_id: int,
    ) -> BuyLeadFile:
        stmt = select(tblbuylead_file)
        stmt = stmt.where(tblbuylead_file.c.file_uuid == import_id)
        if role_id != 1:
            stmt = stmt.where(or_(tblbuylead_file.c.created_by == created_by))
        result = await self.session.execute(stmt)
        return result.mappings().one_or_none()
