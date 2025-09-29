from typing import Annotated

from fastapi import Depends
from sqlalchemy import delete
from src.core.repository import AsyncRepository
from src.core import ID_TYPE
from src.database.database import DbSessionDep, SessionTool


class SessionToolRepository(AsyncRepository[SessionTool]): ...


def get_session_tool_repository(db_session: DbSessionDep) -> SessionToolRepository:
    return SessionToolRepository(SessionTool, db_session)


SessionToolRepositoryDep = Annotated[
    SessionToolRepository,
    Depends(get_session_tool_repository),
]
