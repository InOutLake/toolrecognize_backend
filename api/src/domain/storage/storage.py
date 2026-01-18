from typing import Annotated
from pydantic import EmailStr, Field
from domain.shared import Domain


class Storage(Domain):
    name: Annotated[str, Field(max_length=30)]
    address: Annotated[str, Field(max_length=100)]
