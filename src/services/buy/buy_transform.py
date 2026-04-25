from app import constant
from app.core.logging import logger
from common.schema_types import BuyStatus, clean_str, to_int, validate_mobile
from model.buy.buy import BuyLead


def transform(
    row: dict,
    import_id,
    created_by: str,
    make_map: dict,
    model_map: dict,
    branch_map: dict,
    source: str,
    broker_name: str | None = None,
) -> tuple[BuyLead | None, str | None]:
    # dict | None:
    try:
        cleaned = {}
        for field in constant.BUYREQUIREDCOLUMS:
            raw_value = row.get(field)
            if field in constant.BUYREQUIREDINTCOLUMS:
                value = to_int(raw_value)
            else:
                value = clean_str(raw_value)
            if value is None:
                raise ValueError(f"{constant.MISSINGVALUES} : {field}")
            cleaned[field] = value

        make_name = cleaned["make"]
        model_name = cleaned["model"]
        branch_name = cleaned["branch"]

        make_id = make_map.get(make_name.lower())
        if not make_id:
            raise ValueError(f"{constant.WRONGVALUES} : {make_name}")

        model_id = model_map.get((model_name.lower(), make_id))
        if not model_id:
            raise ValueError(f"{constant.WRONGVALUES} : {make_name} - {model_name}")

        branch_id = branch_map.get(branch_name.lower())
        if not branch_id:
            raise ValueError(f"{constant.WRONGVALUES} : {branch_name}")

        return (
            BuyLead(
                branch=branch_name,
                mobile=validate_mobile(cleaned["mobile"]),
                mode=cleaned["mode"],
                customer_name=cleaned["customer_name"],
                make_id=make_id,
                model_id=model_id,
                fuel_type=cleaned["fuel_type"],
                year=cleaned["year"],
                kms=cleaned["kms"],
                owner=cleaned["owner"],
                client_offer=cleaned["client_offer"],
                our_offer=cleaned["our_offer"],
                remarks=constant.REMARKS,
                import_id=import_id,
                source=source,
                broker_name=broker_name,
                status=BuyStatus.NotAllocated.value,
                created_by=created_by,
            ),
            None,
        )
    except Exception as e:
        logger.error(f"Transform error: {str(e)}")
        logger.error(f"Transform error: {row}")
        return None, str(e)
