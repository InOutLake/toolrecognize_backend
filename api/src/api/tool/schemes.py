from pydantic import BaseModel
from core import BaseDto, Model
from core.schemes import Page


class ToolResponse(BaseDto):
    name: str
    description: str


class ToolPageResponse(Page[ToolResponse]): ...


class ToolFilters(BaseModel):
    name: str | None = None


class ToolCreateDto(BaseModel):
    name: str
    description: str


class ToolUpdateDto(BaseModel):
    name: str | None = None
    description: str | None = None


class ToolDeleteDto(Model): ...
