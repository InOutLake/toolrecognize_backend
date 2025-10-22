from pydantic import BaseModel

from core.schemes import ID_TYPE


class Domain(BaseModel):
    id: ID_TYPE
