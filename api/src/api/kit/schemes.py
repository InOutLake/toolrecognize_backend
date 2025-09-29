from pydantic import BaseModel
from core import BaseDto, Model
from src.core import Page


class KitResponse(BaseDto):
    name: str
    description: str | None = None


class KitPageResponse(Page[KitResponse]): ...


class KitFilters(BaseModel):
    name: str | None = None
    description: str | None = None


class KitCreateDto(BaseModel):
    name: str
    description: str | None = None


class KitUpdateDto(BaseModel):
    name: str | None = None
    description: str | None = None


class KitDeleteDto(Model): ...
