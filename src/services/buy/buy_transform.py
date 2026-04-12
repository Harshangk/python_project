from app import constant
from app.core.logging import logger
from common.schema_types import BuyStatus, clean_str, to_int
from model.buy.buy import BuyLead


def transform(
    row: dict,
    import_id,
    source: str,
    created_by: str,
    make_map: dict,
    model_map: dict,
) -> dict | None:
    try:
        make_name = clean_str(row.get("make"))
        model_name = clean_str(row.get("model"))

        if not make_name or not model_name:
            raise ValueError("Make or Model missing")

        make_id = make_map.get(make_name.lower())
        if not make_id:
            raise ValueError(f"Invalid make: {make_name}")

        model_id = model_map.get((model_name.lower(), make_id))
        if not model_id:
            raise ValueError(f"Invalid model '{model_name}' for make '{make_name}'")

        return BuyLead(
            branch=clean_str(row.get("branch")),
            mobile=clean_str(row.get("mobile")),
            mode=clean_str(row.get("mode")),
            customer_name=clean_str(row.get("customer_name")),
            make_id=make_id,
            model_id=model_id,
            fuel_type=clean_str(row.get("fuel_type")),
            year=clean_str(row.get("year")),
            kms=to_int(row.get("kms")),
            owner=clean_str(row.get("owner")),
            client_offer=to_int(row.get("client_offer")),
            our_offer=to_int(row.get("our_offer")),
            remarks=constant.REMARKS,
            import_id=import_id,
            source=source,
            status=BuyStatus.NotAllocated.value,
            created_by=created_by,
        )
    except Exception as e:
        logger.error(f"Transform error: {str(e)}")
        logger.error(f"Transform error: {row}")
        return None
