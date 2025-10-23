from datetime import datetime
from typing import TypeVar
from pydantic import BaseModel

from core.schemes import ID_TYPE


class Domain(BaseModel):
    id: ID_TYPE
    created_at: datetime | None = None
    updated_at: datetime | None = None


DomainModelT = TypeVar("DomainModelT", bound=Domain)
