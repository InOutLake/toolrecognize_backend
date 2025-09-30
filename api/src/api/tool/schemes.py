from typing import Annotated
from fastapi import Depends, Query
from pydantic import BaseModel
from src.core import BaseDto, Model, Page


class ToolResponse(BaseDto, Model):
    name: str
    description: str


class ToolPageResponse(Page[ToolResponse]): ...


class ToolFilters(BaseModel):
    name: str | None = None


def tool_filters(
    name: Annotated[str | None, Query()] = None,
) -> ToolFilters:
    return ToolFilters(name=name)


ToolFiltersDep = Annotated[ToolFilters, Depends(tool_filters)]


class ToolCreateDto(BaseModel):
    name: str
    description: str


class ToolUpdateDto(BaseModel):
    name: str | None = None
    description: str | None = None


class ToolDeleteDto(Model): ...
