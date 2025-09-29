from typing import Annotated
from fastapi import Depends

from src.core import AsyncRepository
from src.database import DbSessionDep, Tool, ID_TYPE


class ToolRepository(AsyncRepository[Tool]):
    async def list_by_ids(self, ids: list[ID_TYPE]) -> tuple[list[Tool], int]:
        return await self.list(extra_filters=[Tool.id.in__(ids)])


def get_tool_repository(db: DbSessionDep) -> ToolRepository:
    return ToolRepository(Tool, db)


ToolRepositoryDep = Annotated[ToolRepository, Depends(get_tool_repository)]
