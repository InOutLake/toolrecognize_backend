from typing import TypeVar
from pydantic import BaseModel, ConfigDict
from uuid import uuid4
from domain.shared.value_objects.id import ID_TYPE


class Domain(BaseModel):
    id: ID_TYPE = uuid4()
    model_config = ConfigDict(from_attributes=True)


DomainModelT = TypeVar("DomainModelT", bound=Domain)
