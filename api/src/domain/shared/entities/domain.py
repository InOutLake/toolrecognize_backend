from typing import TypeVar
from pydantic import BaseModel
from uuid import uuid4
from src.domain.shared import ID_TYPE


class Domain(BaseModel):
    id: ID_TYPE = uuid4()


DomainModelT = TypeVar("DomainModelT", bound=Domain)
