from typing import Any, Mapping, Sequence
from uuid import UUID

from sqlalchemy import String, and_, asc, cast, delete, desc, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import constant
from auth.exceptions import AllocationError, AlreadyExistsError, CreationError, NotFound
from common.schema_types import (
    BuyDisposition,
    BuyStage,
    BuyStatus,
    Category,
    FileStatus,
    Months,
)
from model.buy.buy import AllocateLeadsRequest
from model.buy.buy import BuyLead as BuyLeadModel
from model.buy.buy import (
    BuyLeadFile,
    BuyLeadFollowup,
    BuyLeadFollowupDetail,
    BuyLeadPayment,
)
from orm.buy.buy import (
    tblbuylead,
    tblbuylead_address,
    tblbuylead_evaluation,
    tblbuylead_evaluation_parameter,
    tblbuylead_evaluation_photo,
    tblbuylead_file,
    tblbuylead_followup,
    tblbuylead_payment,
    tblbuylead_stockin,
    tblbuylead_stockin_document,
    tblbuylead_vehicle,
    tblbuylead_vehicle_insurance,
)
from orm.common.common import (
    mstmake,
    mstmodel,
    mstpart,
    mstsubpart,
    mstsubpartstatus,
    mstsubpartsubstatus,
)
from repository.buy.buy_repository_interface import BuyRepositoryInterface
from repository.buy.buy_search_sort import (
    FOLLOWUP_LEAD_COLUMNS,
    FOLLOWUP_LEAD_SEARCHABLE_COLUMNS,
    IMPORT_LEAD_COLUMNS,
    IMPORT_LEAD_SEARCHABLE_COLUMNS,
    LEAD_COLUMNS,
    LEAD_EVALUATION_PDF_COLUMNS,
    LEAD_PAYMENT_PDF_COLUMNS,
    LEAD_SEARCHABLE_COLUMNS,
    LEAD_SORTABLE_COLUMNS,
)


class BuyRepository(BuyRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def _apply_role_filter(
        self,
        stmt,
        created_by: str,
        role_id: int,
    ):
        if role_id not in constant.ADMIN_ROLE_IDS:

            stmt = stmt.where(
                or_(
                    tblbuylead.c.telecaller == created_by,
                    tblbuylead.c.executive == created_by,
                    tblbuylead.c.created_by == created_by,
                )
            )

        return stmt

    async def get_existing_duplicates(self, keys: list[tuple]):
        """
        keys format:
        [
            ("9876543210", 1, 10),
            ("9999999999", 2, 20),
        ]
        """

        if not keys:
            return set()

        conditions = [
            (
                (tblbuylead.c.mobile == mobile)
                & (tblbuylead.c.make_id == make_id)
                & (tblbuylead.c.model_id == model_id)
            )
            for mobile, make_id, model_id in keys
        ]

        stmt = select(
            tblbuylead.c.mobile,
            tblbuylead.c.make_id,
            tblbuylead.c.model_id,
        ).where(
            and_(
                or_(*conditions),
                tblbuylead.c.status != BuyStatus.StockIn.value,
            )
        )

        result = await self.session.execute(stmt)

        rows = result.fetchall()

        return {(row.mobile, row.make_id, row.model_id) for row in rows}

    async def _check_existing_lead(
        self,
        lead: BuyLeadModel,
        lead_id: int | None = None,
    ):
        conditions = [
            tblbuylead.c.mobile == lead.mobile,
            tblbuylead.c.make_id == lead.make_id,
            tblbuylead.c.model_id == lead.model_id,
            tblbuylead.c.status != BuyStatus.StockIn.value,
            tblbuylead.c.is_active.is_(True),
            tblbuylead.c.is_deleted.is_(False),
        ]

        # Ignore current lead during update
        if lead_id:
            conditions.append(tblbuylead.c.id != lead_id)

        stmt = select(
            tblbuylead.c.id,
            tblbuylead.c.status,
            tblbuylead.c.telecaller,
            tblbuylead.c.executive,
        ).where(and_(*conditions))

        result = await self.session.execute(stmt)

        existing_lead = result.first()

        if existing_lead:
            raise AlreadyExistsError(
                lead_id=existing_lead.id,
                status=existing_lead.status,
                telecaller=existing_lead.telecaller,
                executive=existing_lead.executive,
            )

    async def create_lead(self, lead: BuyLeadModel, created_by: str) -> int:
        try:
            await self._check_existing_lead(lead)

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
                    category=(
                        lead.category.value
                        if lead.category
                        else Category.Individual.value
                    ),
                    customer_name=lead.customer_name,
                    owner_name=(
                        lead.owner_name if lead.owner_name else lead.customer_name
                    ),
                    payment_name=(
                        lead.payment_name if lead.payment_name else lead.customer_name
                    ),
                    make_id=lead.make_id,
                    model_id=lead.model_id,
                    variant=lead.variant,
                    color=lead.color.value if lead.color else None,
                    fuel_type=lead.fuel_type.value,
                    mfg_month=(
                        lead.mfg_month.value if lead.mfg_month else Months.January.value
                    ),
                    mfg_year=str(lead.mfg_year),
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

            await self._check_existing_lead(
                lead,
                lead_id=lead_id,
            )
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
                    mfg_month=Months.January.value,
                    mfg_year=str(lead.mfg_year),
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
                tblbuylead_followup, tblbuylead.c.id == tblbuylead_followup.c.buylead_id
            )
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
        created_by: str,
        role_id: int,
        search: str | None = None,
        buy_status: BuyStatus | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = self._base_lead_query()
        stmt = self._apply_role_filter(
            stmt,
            created_by,
            role_id,
        )
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
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
        buy_status: BuyStatus | None = None,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(tblbuylead)
            .join(mstmake, tblbuylead.c.make_id == mstmake.c.id)
            .join(mstmodel, tblbuylead.c.model_id == mstmodel.c.id)
            .outerjoin(
                tblbuylead_followup, tblbuylead.c.id == tblbuylead_followup.c.buylead_id
            )
            .outerjoin(
                tblbuylead_address, tblbuylead.c.id == tblbuylead_address.c.buylead_id
            )
            .where(tblbuylead.c.is_active)
        )
        stmt = self._apply_role_filter(
            stmt,
            created_by,
            role_id,
        )
        stmt = self._apply_search(stmt, search)
        if buy_status:
            stmt = stmt.where(tblbuylead.c.status == buy_status)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_lead_export(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
        buy_status: BuyStatus | None = None,
        sort_by: str | None = None,
        sort_order: str | None = None,
    ):
        stmt = self._base_lead_query()
        stmt = self._apply_role_filter(stmt, created_by, role_id)
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
        created_by: str,
        role_id: int,
    ) -> BuyLeadModel:
        stmt = self._base_lead_query()
        stmt = self._apply_role_filter(stmt, created_by, role_id)
        stmt = stmt.where(
            tblbuylead.c.id == lead_id,
            tblbuylead.c.is_active.is_(True),
            tblbuylead.c.is_deleted.is_(False),
        )
        result = await self.session.execute(stmt)
        return result.mappings().one_or_none()

    async def remove_lead(self, lead_id: int, created_by: str, role_id: int) -> bool:
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
        stmt = self._apply_role_filter(stmt, created_by, role_id)
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
                    "created_by": created_by,
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
            if reallocate.telecaller:
                update_data["telecaller"] = reallocate.telecaller

            if reallocate.executive:
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

    async def reopen_leads(self, reopen: AllocateLeadsRequest, created_by: str) -> int:
        try:
            update_data = {
                "status": BuyStatus.Allocated.value,
            }

            if reopen.telecaller:
                update_data["telecaller"] = reopen.telecaller

            if reopen.executive:
                update_data["executive"] = reopen.executive

            update_stmt = (
                update(tblbuylead)
                .where(
                    tblbuylead.c.id.in_(reopen.lead_ids),
                    tblbuylead.c.is_active.is_(True),
                    tblbuylead.c.is_deleted.is_(False),
                    tblbuylead.c.status == BuyStatus.Lost.value,
                )
                .values(**update_data)
            )
            result = await self.session.execute(update_stmt)

            update_stmt = (
                update(tblbuylead_followup)
                .where(tblbuylead_followup.c.buylead_id.in_(reopen.lead_ids))
                .values(
                    stage=BuyStage.Fresh.value,
                    disposition=BuyDisposition.Fresh.value,
                    calldate=func.now(),
                    notes=BuyStage.Fresh.value,
                    created_by=created_by,
                )
            )
            await self.session.execute(update_stmt)

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
                    mfg_month=Months.January.value,
                    mfg_year=str(lead.mfg_year),
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
                tblbuylead.c.status != BuyStatus.Lost.value,
                tblbuylead.c.status != BuyStatus.DND.value,
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
        buy_stage: BuyStage | None = None,
    ) -> Sequence[Mapping[str, Any]]:
        stmt = self._base_followup_lead_query(created_by, role_id)

        stmt = self._apply_followup_search(stmt, search)

        if buy_stage:
            stmt = stmt.where(tblbuylead_followup.c.stage == buy_stage)

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
        buy_stage: BuyStage | None = None,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(tblbuylead)
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
                tblbuylead.c.status != BuyStatus.Lost.value,
                tblbuylead.c.status != BuyStatus.DND.value,
            )
        )
        if role_id != 1:
            stmt = stmt.where(
                or_(
                    tblbuylead.c.telecaller == created_by,
                    tblbuylead.c.executive == created_by,
                )
            )

        stmt = self._apply_followup_search(stmt, search)
        if buy_stage:
            stmt = stmt.where(tblbuylead_followup.c.stage == buy_stage)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def get_followup_lead_export(
        self,
        created_by: str,
        role_id: int,
        search: str | None = None,
        buy_stage: BuyStage | None = None,
    ):
        stmt = self._base_followup_lead_query(created_by, role_id)
        stmt = self._apply_followup_search(stmt, search)
        if buy_stage:
            stmt = stmt.where(tblbuylead_followup.c.stage == buy_stage)
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
        try:
            payload = [
                {k: v for k, v in vars(d).items() if not k.startswith("_")}
                for d in data
            ]

            await self.session.execute(
                insert(tblbuylead),
                payload,
            )

            await self.session.commit()

        except IntegrityError:
            await self.session.rollback()
            raise CreationError(constant.DUPLICATE)

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

    async def create_lead_payment(
        self, lead_payment: BuyLeadPayment, created_by: str
    ) -> int:
        try:
            existing_stmt = select(
                tblbuylead.c.id,
            ).where(
                tblbuylead.c.id == lead_payment.buylead_id,
                tblbuylead.c.is_active.is_(True),
                tblbuylead.c.is_deleted.is_(False),
                or_(
                    tblbuylead.c.status == BuyStatus.Appointment.value,
                ),
            )

            result = await self.session.execute(existing_stmt)
            existing = result.fetchone()

            if not existing:
                raise NotFound(constant.NOTFOUND)

            payment_values = dict(
                buylead_id=lead_payment.buylead_id,
                refurb_cost=lead_payment.refurb_cost,
                deal=lead_payment.deal,
                service_charge=lead_payment.service_charge,
                tcs=lead_payment.tcs,
                gst=lead_payment.gst,
                tax=lead_payment.tax,
                rcd=lead_payment.rcd,
                commission=lead_payment.commission,
                deal_with_commission=lead_payment.deal_with_commission,
                deal_without_commission=lead_payment.deal_without_commission,
                token=lead_payment.token,
                cash=lead_payment.cash,
                loan=lead_payment.loan,
                less=lead_payment.less,
                hold=lead_payment.hold,
                ch_rtgs=lead_payment.ch_rtgs,
                total_payble=lead_payment.total_payble,
                remarks=lead_payment.remarks,
                created_by=lead_payment.created_by,
            )
            payment_update_values = {
                key: value
                for key, value in payment_values.items()
                if key != "buylead_id"
            }
            payment_update_values.pop("created_by")
            payment_update_values.update(
                modified_at=func.now(),
                modified_by=created_by,
            )

            stmt = (
                insert(tblbuylead_payment)
                .values(**payment_values)
                .on_conflict_do_update(
                    index_elements=[tblbuylead_payment.c.buylead_id],
                    set_=payment_update_values,
                )
                .returning(tblbuylead_payment.c.id)
            )
            result = await self.session.execute(stmt)
            payment_id = result.scalar_one()

            if lead_payment.lead_vehicle:
                lead_vehicle = lead_payment.lead_vehicle
                vehicle_values = dict(
                    buylead_id=lead_vehicle.buylead_id,
                    registration_no=lead_vehicle.registration_no,
                    transmission=(
                        lead_vehicle.transmission.value
                        if lead_vehicle.transmission
                        else None
                    ),
                    cubic_capacity=lead_vehicle.cubic_capacity,
                    chassis_no=(
                        lead_vehicle.chassis_no if lead_vehicle.chassis_no else None
                    ),
                    engine_no=(
                        lead_vehicle.engine_no if lead_vehicle.engine_no else None
                    ),
                    push_button=(
                        lead_vehicle.push_button.value
                        if lead_vehicle.push_button
                        else None
                    ),
                    company_invoice=(
                        lead_vehicle.company_invoice.value
                        if lead_vehicle.company_invoice
                        else None
                    ),
                    noc=(lead_vehicle.noc.value if lead_vehicle.noc else None),
                    reg_month=(
                        lead_vehicle.reg_month.value if lead_vehicle.reg_month else None
                    ),
                    reg_year=(
                        str(lead_vehicle.reg_year)
                        if lead_vehicle.reg_year is not None
                        else None
                    ),
                    euro=lead_vehicle.euro,
                    rc_book=lead_vehicle.rc_book.value,
                    second_key=lead_vehicle.second_key.value,
                    hypo=lead_vehicle.hypo.value,
                    hypo_bank=lead_vehicle.hypo_bank,
                    service_record=lead_vehicle.service_record.value,
                    puc=lead_vehicle.puc.value,
                    memo=lead_vehicle.memo.value,
                    memo_amount=lead_vehicle.memo_amount,
                    memo_paid=(
                        lead_vehicle.memo_paid.value if lead_vehicle.memo_paid else None
                    ),
                    mv_tax=lead_vehicle.mv_tax,
                    rma=lead_vehicle.rma,
                    taxi_private=lead_vehicle.taxi_private,
                    other_noc=lead_vehicle.other_noc,
                    blacklist=lead_vehicle.blacklist,
                    rto_status=lead_vehicle.rto_status,
                )
                vehicle_update_values = {
                    key: value
                    for key, value in vehicle_values.items()
                    if key != "buylead_id"
                }
                stmt = (
                    insert(tblbuylead_vehicle)
                    .values(**vehicle_values)
                    .on_conflict_do_update(
                        index_elements=[tblbuylead_vehicle.c.buylead_id],
                        set_=vehicle_update_values,
                    )
                )
                await self.session.execute(stmt)

            if lead_payment.lead_vehicle_insurance:
                lead_vehicle_insurance = lead_payment.lead_vehicle_insurance
                vehicle_insurance_values = dict(
                    buylead_id=lead_vehicle_insurance.buylead_id,
                    online_insurance=lead_vehicle_insurance.online_insurance.value,
                    insurance_type=lead_vehicle_insurance.insurance_type.value,
                    cp_zd_company=lead_vehicle_insurance.cp_zd_company,
                    tp_company=lead_vehicle_insurance.tp_company,
                    cp_zd_date=lead_vehicle_insurance.cp_zd_date,
                    tp_date=lead_vehicle_insurance.tp_date,
                    idv=lead_vehicle_insurance.idv,
                    ncb=lead_vehicle_insurance.ncb,
                    premium=lead_vehicle_insurance.premium,
                )
                vehicle_insurance_update_values = {
                    key: value
                    for key, value in vehicle_insurance_values.items()
                    if key != "buylead_id"
                }
                stmt = (
                    insert(tblbuylead_vehicle_insurance)
                    .values(**vehicle_insurance_values)
                    .on_conflict_do_update(
                        index_elements=[
                            tblbuylead_vehicle_insurance.c.buylead_id,
                        ],
                        set_=vehicle_insurance_update_values,
                    )
                )
                await self.session.execute(stmt)

            await self.session.commit()
            return payment_id
        except IntegrityError:
            await self.session.rollback()
            raise CreationError(constant.FAILED)

    async def get_lead_payment_pdf(
        self,
        lead_id: int,
        created_by: str,
        role_id: int,
    ) -> Mapping[str, Any] | None:
        stmt = (
            select(*LEAD_PAYMENT_PDF_COLUMNS)
            .join(mstmake, tblbuylead.c.make_id == mstmake.c.id)
            .join(mstmodel, tblbuylead.c.model_id == mstmodel.c.id)
            .join(
                tblbuylead_payment,
                tblbuylead.c.id == tblbuylead_payment.c.buylead_id,
            )
            .outerjoin(
                tblbuylead_vehicle,
                tblbuylead.c.id == tblbuylead_vehicle.c.buylead_id,
            )
            .outerjoin(
                tblbuylead_vehicle_insurance,
                tblbuylead.c.id == tblbuylead_vehicle_insurance.c.buylead_id,
            )
            .where(
                tblbuylead.c.id == lead_id,
                tblbuylead.c.is_active.is_(True),
                tblbuylead.c.is_deleted.is_(False),
            )
        )

        if role_id != 1:
            stmt = stmt.where(
                or_(
                    tblbuylead.c.telecaller == created_by,
                    tblbuylead.c.executive == created_by,
                    tblbuylead_payment.c.created_by == created_by,
                )
            )

        result = await self.session.execute(stmt)
        return result.mappings().one_or_none()

    async def upsert_evaluation_photos(
        self,
        evaluation_photos: list[dict],
    ) -> int:

        if not evaluation_photos:
            return 0

        lead_id = evaluation_photos[0]["buylead_id"]

        stmt = insert(tblbuylead_evaluation_photo).values(evaluation_photos)

        stmt = stmt.on_conflict_do_update(
            index_elements=[
                tblbuylead_evaluation_photo.c.buylead_id,
                tblbuylead_evaluation_photo.c.photo_name,
            ],
            set_={
                "s3_key": stmt.excluded.s3_key,
                "content_type": stmt.excluded.content_type,
                "modified_by": stmt.excluded.created_by,
                "modified_at": func.now(),
            },
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return lead_id

    async def upsert_stockin_documents(
        self,
        stockin_documents: list[dict],
    ) -> int:
        if not stockin_documents:
            return 0

        lead_id = stockin_documents[0]["buylead_id"]

        stmt = insert(tblbuylead_stockin_document).values(stockin_documents)
        stmt = stmt.on_conflict_do_update(
            index_elements=[
                tblbuylead_stockin_document.c.buylead_id,
                tblbuylead_stockin_document.c.document_name,
            ],
            set_={
                "s3_key": stmt.excluded.s3_key,
                "content_type": stmt.excluded.content_type,
                "modified_by": stmt.excluded.created_by,
                "modified_at": func.now(),
            },
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return lead_id

    async def save_stockin(
        self,
        lead_id: int,
        remarks: str,
        created_by: str,
    ) -> int:
        try:
            stmt = insert(tblbuylead_stockin).values(
                buylead_id=lead_id,
                remarks=remarks,
                created_by=created_by,
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=[tblbuylead_stockin.c.buylead_id],
                set_={
                    "remarks": remarks,
                    "modified_at": func.now(),
                    "modified_by": created_by,
                },
            )
            await self.session.execute(stmt)
            await self.session.commit()
            return lead_id
        except Exception as ex:
            await self.session.rollback()
            raise ex

    async def save_evaluation_parameters(
        self,
        lead_id: int,
        evaluation_parameters: list[dict],
        remarks: str,
        created_by: str,
    ) -> int:
        try:
            delete_stmt = delete(tblbuylead_evaluation_parameter).where(
                tblbuylead_evaluation_parameter.c.buylead_id == lead_id
            )

            await self.session.execute(delete_stmt)
            if evaluation_parameters:
                await self.session.execute(
                    tblbuylead_evaluation_parameter.insert(),
                    evaluation_parameters,
                )
            stmt = insert(tblbuylead_evaluation).values(
                buylead_id=lead_id,
                remarks=remarks,
                created_by=created_by,
            )

            stmt = stmt.on_conflict_do_update(
                index_elements=[tblbuylead_evaluation.c.buylead_id],
                set_={
                    "remarks": remarks,
                    "modified_at": func.now(),
                    "modified_by": created_by,
                },
            )

            await self.session.execute(stmt)
            await self.session.commit()
            return lead_id

        except Exception as ex:
            await self.session.rollback()
            raise ex

    async def get_lead_evaluation_pdf(
        self,
        lead_id: int,
        created_by: str,
        role_id: int,
    ) -> Mapping[str, Any] | None:

        lead_stmt = (
            select(*LEAD_EVALUATION_PDF_COLUMNS)
            .join(
                mstmake,
                tblbuylead.c.make_id == mstmake.c.id,
            )
            .join(
                mstmodel,
                tblbuylead.c.model_id == mstmodel.c.id,
            )
            .join(
                tblbuylead_evaluation,
                tblbuylead.c.id == tblbuylead_evaluation.c.buylead_id,
            )
            .outerjoin(
                tblbuylead_vehicle,
                tblbuylead.c.id == tblbuylead_vehicle.c.buylead_id,
            )
            .outerjoin(
                tblbuylead_vehicle_insurance,
                tblbuylead.c.id == tblbuylead_vehicle_insurance.c.buylead_id,
            )
            .where(
                tblbuylead.c.id == lead_id,
                tblbuylead.c.is_active.is_(True),
                tblbuylead.c.is_deleted.is_(False),
            )
        )

        if role_id != 1:
            lead_stmt = lead_stmt.where(
                or_(
                    tblbuylead.c.telecaller == created_by,
                    tblbuylead.c.executive == created_by,
                    tblbuylead_payment.c.created_by == created_by,
                )
            )

        lead_result = await self.session.execute(lead_stmt)
        lead = lead_result.mappings().one_or_none()

        if not lead:
            return None

        param_stmt = (
            select(
                tblbuylead_evaluation_parameter.c.part_id,
                tblbuylead_evaluation_parameter.c.subpart_id,
                tblbuylead_evaluation_parameter.c.subpartstatus_id,
                tblbuylead_evaluation_parameter.c.subpartsubstatus_id,
                mstpart.c.part_name,
                mstsubpart.c.subpart_name,
                mstsubpartstatus.c.subpart_status,
                mstsubpartsubstatus.c.subpart_sub_status,
            )
            .join(
                mstpart,
                tblbuylead_evaluation_parameter.c.part_id == mstpart.c.id,
            )
            .join(
                mstsubpart,
                and_(
                    tblbuylead_evaluation_parameter.c.part_id == mstsubpart.c.part_id,
                    tblbuylead_evaluation_parameter.c.subpart_id == mstsubpart.c.id,
                ),
            )
            .join(
                mstsubpartstatus,
                and_(
                    tblbuylead_evaluation_parameter.c.subpart_id
                    == mstsubpartstatus.c.subpart_id,
                    tblbuylead_evaluation_parameter.c.subpartstatus_id
                    == mstsubpartstatus.c.id,
                ),
            )
            .join(
                mstsubpartsubstatus,
                and_(
                    tblbuylead_evaluation_parameter.c.subpartstatus_id
                    == mstsubpartsubstatus.c.subpartstatus_id,
                    tblbuylead_evaluation_parameter.c.subpartsubstatus_id
                    == mstsubpartsubstatus.c.id,
                ),
            )
            .where(tblbuylead_evaluation_parameter.c.buylead_id == lead_id)
        )

        param_result = await self.session.execute(param_stmt)
        params = param_result.mappings().all()

        photo_stmt = select(
            tblbuylead_evaluation_photo.c.id,
            tblbuylead_evaluation_photo.c.buylead_id,
            tblbuylead_evaluation_photo.c.s3_key,
            tblbuylead_evaluation_photo.c.photo_name,
        ).where(tblbuylead_evaluation_photo.c.buylead_id == lead_id)

        photo_result = await self.session.execute(photo_stmt)
        photos = photo_result.mappings().all()

        lead = dict(lead)

        lead["evaluation_parameters"] = [
            {
                "part_id": p["part_id"],
                "part_name": p["part_name"],
                "subpart_id": p["subpart_id"],
                "subpart_name": p["subpart_name"],
                "subpart_status": p["subpart_status"],
                "subpart_sub_status": p["subpart_sub_status"],
            }
            for p in params
        ]

        lead["photos"] = [
            {
                "id": p["id"],
                "s3_key": p["s3_key"],
                "photo_name": p["photo_name"],
            }
            for p in photos
        ]

        return lead
