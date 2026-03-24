from contextvars import ContextVar
from uuid import UUID
from enum import Enum

trace_id_var: ContextVar[UUID | None] = ContextVar("trace_id", default=None)


def set_trace_id(trace_id: UUID) -> None:
    trace_id_var.set(trace_id)


def get_trace_id() -> UUID | None:
    return trace_id_var.get()


def enum_to_dict_list(enum_cls: type[Enum]):
    return [{"key": e.name, "value": e.value} for e in enum_cls]
