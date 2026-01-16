from typing import Annotated, TypeVar
from pydantic import BaseModel, ConfigDict, Field
from uuid import uuid4
from domain.shared.value_objects.id import ID_TYPE


class Domain(BaseModel):
    id: Annotated[ID_TYPE, Field(default_factory=uuid4)]
    model_config = ConfigDict(from_attributes=True)


DomainModelT = TypeVar("DomainModelT", bound=Domain)
