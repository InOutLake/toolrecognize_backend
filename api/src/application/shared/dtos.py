from typing import TypeVar

from pydantic import BaseModel

from domain.shared import ID_TYPE


class CreateDto(BaseModel): ...


class UpdateDtoBase(BaseModel): ...


class UpdateDto(UpdateDtoBase):
    id: ID_TYPE


class FiltersDto(BaseModel):
    id: ID_TYPE | None = None


class ResponseDto(BaseModel): ...


class DtoUnset(BaseModel): ...


CreateModelT = TypeVar("CreateModelT", bound=CreateDto)
UpdateBaseModelT = TypeVar("UpdateBaseModelT", bound=UpdateDtoBase)
UpdateModelT = TypeVar("UpdateModelT", bound=UpdateDto)
FiltersModelT = TypeVar("FiltersModelT", bound=FiltersDto)
ResponseModelT = TypeVar("ResponseModelT", bound=ResponseDto)
