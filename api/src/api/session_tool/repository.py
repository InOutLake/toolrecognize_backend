from typing import Annotated

from fastapi import Depends
from sqlalchemy import select, delete
from src.core.repository import AsyncRepository
from src.core.schemes import ID_TYPE
from src.database.database import DbSessionDep, SessionTool


class SessionToolRepository(AsyncRepository[SessionTool]):
    async def add_tools_to_session(
        self, session_id: ID_TYPE, tools_recognized: dict[ID_TYPE, int]
    ):
        """Insert tools_recognized into session_tools table"""
        # First, clear any existing tools for this session
        await self.session.execute(
            delete(SessionTool).where(SessionTool.session_id == session_id)
        )
        
        # Then insert the recognized tools
        for tool_id, quantity in tools_recognized.items():
            session_tool = SessionTool(
                session_id=session_id,
                tool_id=tool_id,
                quantity_given=quantity,
                quantity_returned=0  # Initially 0, will be updated when tools are returned
            )
            self.session.add(session_tool)
        
        await self.session.commit()


def get_session_tool_repository(db_session: DbSessionDep) -> SessionToolRepository:
    return SessionToolRepository(SessionTool, db_session)


SessionToolRepositoryDep = Annotated[
    SessionToolRepository,
    Depends(get_session_tool_repository),
]
