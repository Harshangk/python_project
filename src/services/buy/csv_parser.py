import csv
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, IO, TypeVar

from api.schema_types import BuyMode, Color, FuelType, Owner
from app import constant
from model.buy.buy import BuyLead as BuyLeadModel, BuyLeadAddress
from repository.buy.buy_repository_interface import BuyRepositoryInterface

T = TypeVar("T")


class ParsingError(Exception):
    pass


@dataclass
class ParsedRowResult(Generic[T]):
    row_number: int
    row: dict[str, str]
    parsed: T | None = None
    error: str | None = None


class BaseCSVParser(ABC, Generic[T]):
    REQUIRED_FIELDNAMES: tuple[str, ...] = ()
    OPTIONAL_FIELDS: tuple[str, ...] = ()

    def __init__(self, file: IO[str]) -> None:
        self.file = file
        self.headers: list[str] = []

    def parse_rows(self) -> list[tuple[int, dict[str, str]]]:
        reader = csv.DictReader(self.file)
        if not reader.fieldnames:
            raise ParsingError("CSV header is missing.")

        self.headers = [header.strip().lower() if header else "" for header in reader.fieldnames]
        if any(header == "" for header in self.headers):
            raise ParsingError("CSV contains an empty header column.")

        missing_headers = sorted(set(self.REQUIRED_FIELDNAMES) - set(self.headers))
        if missing_headers:
            raise ParsingError(f"Missing required CSV columns: {', '.join(missing_headers)}.")

        rows = [
            (index, self._normalize_row(row))
            for index, row in enumerate(reader, start=2)
        ]
        if not rows:
            raise ParsingError("CSV file must contain at least one data row.")

        return rows

    @staticmethod
    def _normalize_row(row: dict[str, str | None]) -> dict[str, str]:
        return {
            (key.strip().lower() if key else ""): (value.strip() if value else "")
            for key, value in row.items()
        }

    @abstractmethod
    async def parse(self) -> list[ParsedRowResult[T]]:
        raise NotImplementedError


class BuyLeadCSVParser(BaseCSVParser[BuyLeadModel]):
    REQUIRED_FIELDNAMES = tuple(sorted(constant.REQUIRED_IMPORT_FIELDS))
    OPTIONAL_FIELDS = tuple(sorted(constant.OPTIONAL_IMPORT_FIELDS))

    def __init__(
        self,
        file: IO[str],
        buy_repository: BuyRepositoryInterface,
        source: str,
        broker_name: str | None = None,
    ) -> None:
        super().__init__(file=file)
        self.buy_repository = buy_repository
        self.source = source
        self.broker_name = broker_name
        self.valid_modes = {mode.value.lower(): mode for mode in BuyMode}
        self.valid_fuel_types = {fuel_type.value.lower(): fuel_type for fuel_type in FuelType}
        self.valid_colors = {color.value.lower(): color for color in Color}
        self.valid_owners = {owner.value for owner in Owner}

    async def parse(self) -> list[ParsedRowResult[BuyLeadModel]]:
        parsed_rows = self.parse_rows()
        make_keys = {
            row["make"].strip().lower()
            for _, row in parsed_rows
            if row.get("make")
        }
        make_id_map = await self.buy_repository.get_make_ids_by_names(make_keys)
        model_id_map = await self.buy_repository.get_model_ids_by_make_ids(set(make_id_map.values()))

        results: list[ParsedRowResult[BuyLeadModel]] = []
        for row_number, row in parsed_rows:
            try:
                parsed = self._parse_row(
                    row=row,
                    make_id_map=make_id_map,
                    model_id_map=model_id_map,
                )
                results.append(ParsedRowResult(row_number=row_number, row=row, parsed=parsed))
            except ParsingError as ex:
                results.append(
                    ParsedRowResult(
                        row_number=row_number,
                        row=row,
                        error=str(ex),
                    )
                )
        return results

    def _parse_row(
        self,
        row: dict[str, str],
        make_id_map: dict[str, int],
        model_id_map: dict[tuple[int, str], int],
    ) -> BuyLeadModel:
        errors: list[str] = []

        def add_error(message: str) -> None:
            errors.append(message)

        for field in self.REQUIRED_FIELDNAMES:
            if not row.get(field):
                add_error(f"'{field}' is required.")

        customer_name = row.get("customer_name", "")
        if customer_name and not (1 <= len(customer_name) <= 255):
            add_error("'customer_name' must be between 1 to 255 characters.")

        mobile = row.get("mobile", "")
        if mobile and not constant.MOBILE_PATTERN.fullmatch(mobile):
            add_error("'mobile' must start with 0 or 9 and contain exactly 10 digits.")

        alternate_mobile = row.get("alternate_mobile") or None
        if alternate_mobile and not constant.MOBILE_PATTERN.fullmatch(alternate_mobile):
            add_error("'alternate_mobile' must start with 0 or 9 and contain exactly 10 digits.")

        mode = None
        mode_value = row.get("mode", "")
        if mode_value:
            mode = self.valid_modes.get(mode_value.lower())
            if mode is None:
                add_error(f"'mode' must be one of {', '.join(sorted(self.valid_modes))}.")

        fuel_type = None
        fuel_type_value = row.get("fuel_type", "")
        if fuel_type_value:
            fuel_type = self.valid_fuel_types.get(fuel_type_value.lower())
            if fuel_type is None:
                add_error(
                    f"'fuel_type' must be one of {', '.join(sorted(self.valid_fuel_types))}."
                )

        year_value = row.get("year", "")
        if year_value and not constant.YEAR_PATTERN.fullmatch(year_value):
            add_error("'year' must be a 4-digit value.")

        kms = self._parse_int(row.get("kms"), "kms", errors)
        if kms is not None and kms < 0:
            add_error("'kms' must be zero or greater.")

        our_offer = self._parse_int(row.get("our_offer"), "our_offer", errors)
        client_offer = self._parse_optional_int(
            row.get("client_offer"),
            "client_offer",
            errors,
            default=0,
        )

        owner = row.get("owner", "")
        if owner and owner not in self.valid_owners:
            add_error(f"'owner' must be one of {', '.join(sorted(self.valid_owners))}.")

        variant = row.get("variant") or None
        telecaller = row.get("telecaller") or None
        executive = row.get("executive") or None

        color_value = row.get("color", "").lower()
        color = None
        if color_value:
            color = self.valid_colors.get(color_value)
            if color is None:
                add_error(f"'color' must be one of {', '.join(sorted(self.valid_colors))}.")

        make_name = row.get("make", "")
        make_id = None
        if make_name:
            make_id = make_id_map.get(make_name.lower())
            if make_id is None:
                add_error(f"'make' '{make_name}' does not exist.")

        model_name = row.get("model", "")
        model_id = None
        if make_id is not None and model_name:
            model_id = model_id_map.get((make_id, model_name.lower()))
            if model_id is None:
                add_error(f"'model' '{model_name}' does not exist for make '{make_name}'.")

        lead_address = self._build_address(row, errors)

        if errors:
            raise ParsingError(" | ".join(errors))

        return BuyLeadModel(
            branch=row["branch"],
            mobile=mobile,
            alternate_mobile=alternate_mobile,
            source=self.source,
            mode=mode,
            broker_name=self.broker_name,
            customer_name=customer_name,
            make_id=make_id,
            model_id=model_id,
            variant=variant,
            color=color,
            fuel_type=fuel_type,
            year=int(year_value),
            kms=kms,
            owner=owner,
            client_offer=client_offer,
            our_offer=our_offer,
            remarks="Imported from CSV",
            telecaller=telecaller,
            executive=executive,
            lead_address=lead_address,
        )

    def _build_address(self, row: dict[str, str], errors: list[str]) -> BuyLeadAddress | None:
        address = row.get("address") or None
        state = row.get("state") or None
        city = row.get("city") or None
        area = row.get("area") or None
        pincode_raw = row.get("pincode") or None

        if not any([address, state, city, area, pincode_raw]):
            return None

        pincode = None
        if pincode_raw:
            if not constant.PINCODE_PATTERN.fullmatch(pincode_raw):
                errors.append("'pincode' must be a 6-digit value.")
            else:
                pincode = int(pincode_raw)

        return BuyLeadAddress(
            address=address,
            state=state,
            city=city,
            area=area,
            pincode=pincode,
        )

    @staticmethod
    def _parse_int(value: str | None, field_name: str, errors: list[str]) -> int | None:
        if not value:
            return None
        try:
            return int(value)
        except ValueError:
            errors.append(f"'{field_name}' must be an integer.")
            return None

    @staticmethod
    def _parse_optional_int(
        value: str | None,
        field_name: str,
        errors: list[str],
        default: int,
    ) -> int:
        if not value:
            return default
        try:
            return int(value)
        except ValueError:
            errors.append(f"'{field_name}' must be an integer.")
            return default
