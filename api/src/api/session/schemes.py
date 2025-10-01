from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel

from src.core import ID_TYPE, BaseDto, Model, Page
from src.database import SessionStatus


class SessionResponse(Model, BaseDto):
    reciever_id: ID_TYPE
    location_id: ID_TYPE
    kit_id: ID_TYPE
    status: SessionStatus


class SessionToolDto(BaseModel):
    tool_name: str

    quantity_given: int
    quantity_returned: int
    quantity_required: int


class SessionDetailsResponse(SessionResponse):
    given_image_url: str | None = None
    returned_image_url: str | None = None
    tools: list[SessionToolDto] | None = None


class SessionPageResponse(Page[SessionResponse]): ...


class SessionFilters(BaseModel):
    reciever_id: int | None = None
    location_id: int | None = None
    kit_id: int | None = None
    status: SessionStatus | None = None
    opened_from: str | None = None
    opened_to: str | None = None
    returned_from: str | None = None
    returned_to: str | None = None


def session_filters(
    reciever_id: Annotated[int | None, Query()] = None,
    location_id: Annotated[int | None, Query()] = None,
    kit_id: Annotated[int | None, Query()] = None,
    status: Annotated[SessionStatus | None, Query()] = None,
    opened_from: Annotated[str | None, Query()] = None,
    opened_to: Annotated[str | None, Query()] = None,
    returned_from: Annotated[str | None, Query()] = None,
    returned_to: Annotated[str | None, Query()] = None,
) -> SessionFilters:
    return SessionFilters(
        reciever_id=reciever_id,
        location_id=location_id,
        kit_id=kit_id,
        status=status,
        opened_from=opened_from,
        opened_to=opened_to,
        returned_from=returned_from,
        returned_to=returned_to,
    )


SessionFiltersDep = Annotated[SessionFilters, Depends(session_filters)]


class SessionCreateDto(BaseModel):
    reciever_id: int
    location_id: int
    kit_id: int


class SessionUpdateDto(Model):
    reciever_id: int | None = None
    location_id: int | None = None
    kit_id: int | None = None
    status: SessionStatus | None = None
    opened_at: str | None = None
    returned_at: str | None = None
    given_image_url: str | None = None
    returned_image_url: str | None = None
