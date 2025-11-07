from typing import Annotated

from fastapi import Depends, Query
from pydantic import BaseModel

from domain.shared import ID_TYPE


class CreateDto(BaseModel): ...


class UpdateDto(BaseModel):
    id: ID_TYPE


class FiltersDto(BaseModel):
    id: ID_TYPE | None = None


class ResponseDto(BaseModel): ...
