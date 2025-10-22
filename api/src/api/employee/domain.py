from pydantic import EmailStr, Field

from src.core import Domain


class Employee(Domain):
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: EmailStr
