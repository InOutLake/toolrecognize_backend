from enum import StrEnum, auto


class SessionStatus(StrEnum):
    CREATED = auto()
    OPEN_WAITING_FOR_APPROVAL = auto()
    OPENED = auto()
    CLOSE_WAITING_FOR_APPROVAL = auto()
    CLOSED = auto()
