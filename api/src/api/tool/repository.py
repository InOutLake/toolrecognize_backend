from typing import Annotated
from fastapi import Depends

from core.repository import AsyncRepository
from core.schemes import ID_TYPE
from src.database.database import DbSessionDep, Tool


class ToolRepository(AsyncRepository[Tool]):
    async def list_by_ids(self, ids: list[ID_TYPE]) -> tuple[list[Tool], int]:
        return await self.list(extra_filters=[Tool.id.in__(ids)])


def get_tool_repository(db: DbSessionDep) -> ToolRepository:
    return ToolRepository(Tool, db)


ToolRepositoryDep = Annotated[ToolRepository, Depends(get_tool_repository)]
