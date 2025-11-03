from typing import Annotated
from fastapi import Depends
from sqlalchemy import func, select
from src.infrastructure.database import (
    Session as SessionDB,
    DbSessionDep,
    Kit,
    Tool,
    ToolInKit,
)
from src.infrastructure.database import SessionTool as SessionToolDB
from domain.shared import ID_TYPE
from domain.session import Session, SessionTool
from .repository import RepositoryProtocol, SqlAlchemyRepository


class SessionToolRepositoryProtocol(RepositoryProtocol[SessionTool, SessionToolDB]):
    async def session_tools_info(self, session_id: ID_TYPE) -> list[SessionTool]: ...


class SessionToolRepository(
    SessionToolRepositoryProtocol,
    SqlAlchemyRepository[SessionTool, SessionToolDB],
):
    async def session_tools_info(self, session_id: ID_TYPE) -> list[SessionTool]:
        stmt = (
            select(
                SessionDB.id.label("session_id"),
                Tool.id.label("tool_id"),
                Tool.name.label("tool_name"),
                func.coalesce(SessionTool.quantity_given, 0).label("quantity_given"),
                func.coalesce(SessionTool.quantity_returned, 0).label(
                    "quantity_returned"
                ),
                func.coalesce(ToolInKit.quantity, 0).label("quantity_required"),
            )
            .join(Kit, Kit.id == Session.kit_id)
            .join(ToolInKit, ToolInKit.kit_id == Kit.id)
            .join(Tool, Tool.id == ToolInKit.tool_id)
            .outerjoin(
                SessionToolDB,
                (SessionToolDB.session_id == Session.id)
                & (SessionToolDB.tool_id == Tool.id),
            )
            .where(SessionDB.id == session_id)
        )
        result = await self.session.execute(stmt)
        session_tools = result.all()
        return [SessionTool.model_validate(tool) for tool in session_tools]


def get_session_repository(db: DbSessionDep) -> SessionToolRepositoryProtocol:
    return SessionToolRepository(SessionTool, SessionToolDB, db)


SessionToolRepositoryDep = Annotated[
    SessionToolRepositoryProtocol,
    Depends(get_session_repository),
]
