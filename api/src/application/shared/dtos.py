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


CreateModelT = TypeVar("CreateModelT", bound=CreateDto, covariant=True)
UpdateBaseModelT = TypeVar("UpdateBaseModelT", bound=UpdateDtoBase)
UpdateModelT = TypeVar("UpdateModelT", bound=UpdateDto, covariant=True)
FiltersModelT = TypeVar("FiltersModelT", bound=FiltersDto)
ResponseModelT = TypeVar("ResponseModelT", bound=ResponseDto)
