from pydantic import EmailStr, Field
from .base import Entity
from src.domain.value_objects import ID


class Employee(Entity[ID]):
    # Technicaly all the fields must be exclusively typed with ValueObject subtypes
    # with defined validation methods (for example, length of the name).
    # Due to excessful robustness of such action for small project I leave fields as simple types.
    id_: ID
    first_name: str = Field(max_length=100)
    last_name: str = Field(max_length=100)
    email: EmailStr
