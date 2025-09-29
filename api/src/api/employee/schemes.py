from pydantic import BaseModel
from core import BaseDto, Model
from core.schemes import Page


class EmployeeResponse(BaseDto):
    name: str


class EmployeePageResponse(Page[EmployeeResponse]): ...


class EmployeeFilters(BaseModel):
    name: str | None = None


class EmployeeCreateDto(BaseModel):
    name: str


class EmployeeUpdateDto(BaseModel):
    name: str | None = None


class EmployeeDeleteDto(Model): ...
