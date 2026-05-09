from pydantic.dataclasses import dataclass


@dataclass
class Make:
    make: str


@dataclass
class Model:
    make_id: int
    model: str


@dataclass
class Branch:
    branch: str


@dataclass
class Source:
    source: str


@dataclass
class Year:
    year: str


@dataclass
class Broker:
    broker: str


@dataclass
class State:
    state: str


@dataclass
class City:
    state_id: int
    city: str


@dataclass
class Bank:
    bank_name: str


@dataclass
class InsuranceCompany:
    insurance_company_name: str


@dataclass
class Part:
    part_name: str


@dataclass
class SubPart:
    part_id: int
    subpart_name: str


@dataclass
class SubPartStatus:
    subpart_id: int
    subpart_status: str
    is_default: bool


@dataclass
class SubPartSubStatus:
    subpartstatus_id: int
    subpart_sub_status: str
