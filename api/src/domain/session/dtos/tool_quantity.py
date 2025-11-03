from domain.shared import ID_TYPE
from pydantic import BaseModel


class ToolQuantity(BaseModel):
    tool_id: ID_TYPE
    quantity: int
