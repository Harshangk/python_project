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
