from datetime import datetime
from typing import Annotated
from typing import Optional, TypeVar
from pydantic import BaseModel, Field 

ID_TYPE = int

class BaseDto(BaseModel): 
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

class Model(BaseModel):
    id: ID_TYPE

class DtoModel(BaseDto, BaseModel):
    ...

T = TypeVar("T", bound=BaseModel)
class Page[T](BaseModel):
    items: list[T]
    page_number: int
    page_size: int

class PageRequest(BaseModel):
    page_number: int
    page_size: Annotated[int, Field(alias="limit")]

    @property
    def offset(self):
        return self.page_number * self.page_size

