from typing import Annotated
from fastapi import Depends, Query
from pydantic import BaseModel

from src.core import BaseDto, Model, Page


class KitResponse(BaseDto, Model):
    name: str
    description: str | None = None


class KitPageResponse(Page[KitResponse]): ...


class KitFilters(BaseModel):
    name: str | None = None
    description: str | None = None


def kit_filters(
    name: Annotated[str | None, Query()] = None,
    description: Annotated[str | None, Query()] = None,
) -> KitFilters:
    return KitFilters(name=name, description=description)


KitFiltersDep = Annotated[KitFilters, Depends(kit_filters)]


class KitCreateDto(BaseModel):
    name: str
    description: str | None = None


class KitUpdateDto(BaseModel):
    name: str | None = None
    description: str | None = None


class KitDeleteDto(Model): ...
