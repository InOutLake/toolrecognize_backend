from pydantic import BaseModel
from core import BaseDto, Model
from core.schemes import Page


class LocationResponse(BaseDto):
    name: str
    address: str


class LocationPageResponse(Page[LocationResponse]): ...


class LocationFilters(BaseModel):
    name: str | None = None
    address: str | None = None


class LocationCreateDto(BaseModel):
    name: str
    address: str


class LocationUpdateDto(BaseModel):
    name: str | None = None
    address: str | None = None


class LocationDeleteDto(Model): ...
