from pydantic import BaseModel
from core import BaseDto, Model
from src.core import ID_TYPE, Page
from src.database import SessionStatus


class SessionResponse(Model, BaseDto):
    receiver_id: ID_TYPE
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
    receiver_id: int | None = None
    location_id: int | None = None
    kit_id: int | None = None
    status: SessionStatus | None = None
    opened_from: str | None = None
    opened_to: str | None = None
    returned_from: str | None = None
    returned_to: str | None = None


class SessionCreateDto(BaseModel):
    receiver_id: int
    location_id: int
    kit_id: int


class SessionUpdateDto(Model):
    receiver_id: int | None = None
    location_id: int | None = None
    kit_id: int | None = None
    status: SessionStatus | None = None
    opened_at: str | None = None
    returned_at: str | None = None
    given_image_url: str | None = None
    returned_image_url: str | None = None
