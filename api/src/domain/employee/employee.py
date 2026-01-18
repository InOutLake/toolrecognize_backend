from typing import Annotated
from pydantic import EmailStr, Field
from domain.shared import Domain


class Employee(Domain):
    first_name: Annotated[str, Field(max_length=30)]
    last_name: Annotated[str, Field(max_length=30)]
    email: EmailStr
