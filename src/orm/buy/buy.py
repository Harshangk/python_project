from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Identity,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from common.db import mapper_registry
from model.buy import buy as BuyModel

tblbuylead = Table(
    "tblbuylead",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("branch", String(50), nullable=False),
    Column("mobile", String(15), nullable=False),
    Column("alternate_mobile", String(15), nullable=True),
    Column("source", String(50), nullable=False),
    Column("mode", String(25), nullable=False),
    Column("broker_name", String(255), nullable=True),
    Column("category", String(25), nullable=False),
    Column("customer_name", String(255), nullable=False),
    Column("owner_name", String(255), nullable=False),
    Column("payment_name", String(255), nullable=False),
    Column("make_id", Integer, ForeignKey("mstmake.id"), nullable=False),
    Column("model_id", Integer, ForeignKey("mstmodel.id"), nullable=False),
    Column("variant", String(255), nullable=True),
    Column("color", String(50), nullable=True),
    Column("fuel_type", String(50), nullable=False),
    Column("mfg_month", String(9), nullable=False),
    Column("mfg_year", String(4), nullable=False),
    Column("kms", Integer, nullable=False),
    Column("owner", String(1), nullable=False),
    Column("client_offer", Integer, server_default=text("0"), nullable=False),
    Column("our_offer", Integer, server_default=text("0"), nullable=False),
    Column("status", String(25), nullable=False),
    Column("telecaller", String(50), nullable=True),
    Column("executive", String(50), nullable=True),
    Column("remarks", String(500), nullable=False),
    Column("allocated_at", DateTime, nullable=True),
    Column("allocated_by", String(length=50), nullable=True),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    Column("is_active", Boolean, server_default=text("true"), nullable=False),
    Column("is_deleted", Boolean, server_default=text("false"), nullable=False),
    Column("import_id", UUID(as_uuid=True), nullable=True),
    Index("idx_tblbuylead_branch", "branch"),
    Index("idx_tblbuylead_mobile", "mobile"),
    Index("idx_tblbuylead_status", "status"),
    Index("idx_tblbuylead_telecaller", "telecaller"),
    Index("idx_tblbuylead_executive", "executive"),
)

tblbuylead_address = Table(
    "tblbuylead_address",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("address", String(100), nullable=False),
    Column("state", String(25), nullable=False),
    Column("city", String(25), nullable=False),
    Column("area", String(25), nullable=False),
    Column("pincode", Integer(), nullable=True),
    UniqueConstraint("buylead_id", name="uq_tblbuylead_address_buylead_id"),
)

tblbuylead_followup = Table(
    "tblbuylead_followup",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("stage", String(25), nullable=False),
    Column("disposition", String(50), nullable=False),
    Column("calldate", DateTime, nullable=True),
    Column("preferred_time", String(20), nullable=True),
    Column("notes", String(500), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    UniqueConstraint("buylead_id", name="uq_tblbuylead_followup_buylead_id"),
)

tblbuylead_file = Table(
    "tblbuylead_file",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("s3_key", Text(), nullable=False),
    Column("file_status", String(10), nullable=False),
    Column("file_uuid", UUID(as_uuid=True), nullable=False),
    Column("processed_records", Integer, server_default=text("0"), nullable=False),
    Column("error_records", Integer, server_default=text("0"), nullable=False),
    Column("error_s3_key", Text(), nullable=True),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    UniqueConstraint("file_uuid", name="uq_tblbuylead_file_file_uuid"),
    Index("idx_tblbuylead_file_file_uuid", "file_uuid"),
)

tblbuylead_payment = Table(
    "tblbuylead_payment",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("refurb_cost", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("deal", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column(
        "service_charge", Numeric(12, 2), server_default=text("0.00"), nullable=False
    ),
    Column("tcs", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("gst", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("tax", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("rcd", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("commission", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column(
        "deal_with_commission",
        Numeric(12, 2),
        server_default=text("0.00"),
        nullable=False,
    ),
    Column(
        "deal_without_commission",
        Numeric(12, 2),
        server_default=text("0.00"),
        nullable=False,
    ),
    Column("token", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("cash", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("loan", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("less", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("hold", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("ch_rtgs", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("total_payble", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("remarks", String(500), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    UniqueConstraint("buylead_id", name="uq_tblbuylead_payment_buylead_id"),
)

tblbuylead_vehicle = Table(
    "tblbuylead_vehicle",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("registration_no", String(12), nullable=False),
    Column("transmission", String(8), nullable=False),
    Column("cubic_capacity", Integer, server_default=text("0"), nullable=False),
    Column("chassis_no", String(50), nullable=True),
    Column("engine_no", String(50), nullable=True),
    Column("push_button", String(3), nullable=True),
    Column("company_invoice", String(3), nullable=True),
    Column("noc", String(3), nullable=True),
    Column("reg_month", String(9), nullable=True),
    Column("reg_year", String(4), nullable=True),
    Column("euro", String(4), nullable=True),
    Column("rc_book", String(3), nullable=True),
    Column("second_key", String(3), nullable=True),
    Column("hypo", String(3), nullable=True),
    Column("hypo_bank", String(255), nullable=True),
    Column("service_record", String(3), nullable=True),
    Column("puc", String(3), nullable=True),
    Column("memo", String(3), nullable=True),
    Column("memo_amount", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("memo_paid", String(8), nullable=True),
    Column("mv_tax", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("rma", String(8), nullable=True),
    Column("taxi_private", String(8), nullable=True),
    Column("other_noc", String(8), nullable=True),
    Column("blacklist", String(8), nullable=True),
    Column("rto_status", String(8), nullable=True),
    UniqueConstraint("buylead_id", name="uq_tblbuylead_vehicle_buylead_id"),
)

tblbuylead_vehicle_insurance = Table(
    "tblbuylead_vehicle_insurance",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("online_insurance", String(3), nullable=False),
    Column("insurance_type", String(6), nullable=False),
    Column("cp_zd_company", String(255), nullable=True),
    Column("tp_company", String(255), nullable=True),
    Column("cp_zd_date", DateTime, nullable=True),
    Column("tp_date", DateTime, nullable=True),
    Column("idv", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("ncb", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("premium", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    UniqueConstraint("buylead_id", name="uq_tblbuylead_vehicle_insurance_buylead_id"),
)

tblbuylead_evaluation = Table(
    "tblbuylead_evaluation",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("remarks", String(500), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    UniqueConstraint("buylead_id", name="uq_tblbuylead_evaluation_buylead_id"),
)

tblbuylead_evaluation_photo = Table(
    "tblbuylead_evaluation_photo",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("photo_name", String(50), nullable=False),
    Column("s3_key", Text(), nullable=False),
    Column("content_type", String(100), nullable=True),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    UniqueConstraint(
        "buylead_id",
        "photo_name",
        name="uq_tblbuylead_evaluation_photo_buylead_id_photo_name",
    ),
)

tblbuylead_stockin = Table(
    "tblbuylead_stockin",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("remarks", String(500), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    UniqueConstraint("buylead_id", name="uq_tblbuylead_stockin_buylead_id"),
)

tblbuylead_stockin_document = Table(
    "tblbuylead_stockin_document",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("document_name", String(50), nullable=False),
    Column("s3_key", Text(), nullable=False),
    Column("content_type", String(100), nullable=True),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    UniqueConstraint(
        "buylead_id",
        "document_name",
        name="uq_tblbuylead_stockin_document_buylead_id_document_name",
    ),
)

tblbuylead_target = Table(
    "tblbuylead_target",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("user_name", String(50), nullable=False),
    Column("month", String(9), nullable=False),
    Column("year", String(4), nullable=False),
    Column("normal", Integer, server_default=text("0"), nullable=False),
    Column("premium", Integer, server_default=text("0"), nullable=False),
    Column("total", Integer, server_default=text("0"), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Column("modified_at", DateTime, nullable=True),
    Column("modified_by", String(length=50), nullable=True),
    UniqueConstraint(
        "user_name",
        "month",
        "year",
        name="uq_tblbuylead_target_user_month_year",
    ),
    Index("idx_tblbuylead_target_user_name", "user_name"),
    Index("idx_tblbuylead_target_month", "month"),
    Index("idx_tblbuylead_target_year", "year"),
)

tblbuylead_evaluation_parameter = Table(
    "tblbuylead_evaluation_parameter",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("part_id", Integer, ForeignKey("mstpart.id"), nullable=False),
    Column("subpart_id", Integer, ForeignKey("mstsubpart.id"), nullable=False),
    Column(
        "subpartstatus_id",
        Integer,
        ForeignKey("mstsubpartstatus.id"),
        nullable=False,
    ),
    Column(
        "subpartsubstatus_id",
        Integer,
        ForeignKey("mstsubpartsubstatus.id"),
        nullable=True,
    ),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
    Index("idx_tblbuylead_evaluation_parameter_buylead_id", "buylead_id"),
)

tblbuylead_preprice = Table(
    "tblbuylead_preprice",
    mapper_registry.metadata,
    Column("id", Integer, Identity(), primary_key=True, autoincrement=True),
    Column("buylead_id", Integer, ForeignKey("tblbuylead.id"), nullable=False),
    Column("pre_price", Numeric(12, 2), server_default=text("0.00"), nullable=False),
    Column("remarks", String(500), nullable=False),
    Column("created_at", DateTime, server_default=text("now()"), nullable=False),
    Column("created_by", String(length=50), nullable=False),
)


def start_mappers() -> None:
    mapper_registry.map_imperatively(BuyModel.BuyLead, tblbuylead)
    mapper_registry.map_imperatively(BuyModel.BuyLeadAddress, tblbuylead_address)
    mapper_registry.map_imperatively(BuyModel._BuyLeadFollowup, tblbuylead_followup)
    mapper_registry.map_imperatively(BuyModel.BuyLeadFile, tblbuylead_file)
    mapper_registry.map_imperatively(BuyModel.BuyLeadPayment, tblbuylead_payment)
    mapper_registry.map_imperatively(BuyModel.BuyLeadVehicle, tblbuylead_vehicle)
    mapper_registry.map_imperatively(
        BuyModel.BuyLeadVehicleInsurance, tblbuylead_vehicle_insurance
    )
    mapper_registry.map_imperatively(
        BuyModel.BuyLeadEvaluationPhoto, tblbuylead_evaluation_photo
    )
    mapper_registry.map_imperatively(BuyModel.BuyLeadStockin, tblbuylead_stockin)
    mapper_registry.map_imperatively(
        BuyModel.BuyLeadStockinDocument, tblbuylead_stockin_document
    )
    mapper_registry.map_imperatively(BuyModel.BuyLeadTarget, tblbuylead_target)
    mapper_registry.map_imperatively(
        BuyModel.BuyLeadEvaluationParameter, tblbuylead_evaluation_parameter
    )
    mapper_registry.map_imperatively(BuyModel.BuyLeadPreprice, tblbuylead_preprice)


def stop_mappers() -> None:
    mapper_registry.dispose()
