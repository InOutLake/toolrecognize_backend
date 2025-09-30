from typing import Annotated
from fastapi import Depends, Query
from pydantic import BaseModel
from src.core import Page, BaseDto, Model


class LocationResponse(BaseDto, Model):
    name: str
    address: str


class LocationPageResponse(Page[LocationResponse]): ...


class LocationFilters(BaseModel):
    name: str | None = None
    address: str | None = None


def location_filters(
    name: Annotated[str | None, Query()] = None,
    address: Annotated[str | None, Query()] = None,
) -> LocationFilters:
    return LocationFilters(name=name, address=address)


LocationFiltersDep = Annotated[LocationFilters, Depends(location_filters)]


class LocationCreateDto(BaseModel):
    name: str
    address: str


class LocationUpdateDto(BaseModel):
    name: str | None = None
    address: str | None = None


class LocationDeleteDto(Model): ...
