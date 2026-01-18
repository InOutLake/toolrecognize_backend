from typing import Annotated

from fastapi import Depends
from sqlalchemy import func, select

from application.shared.dtos import UpdateDto
from domain.session import Session, SessionTool
from domain.shared import ID_TYPE
from infrastructure.repositories.sqlalchemy_repository import SqlAlchemyRepository
from shared.interfaces.repository import RepositoryProtocol
from infrastructure.database import (
    DbSessionDep,
    Kit,
    Tool,
    ToolInKit,
)
from infrastructure.database import (
    Session as SessionDB,
)
from infrastructure.database import SessionTool as SessionToolDB


class SessionToolUpdateDto(UpdateDto):
    tool_id: ID_TYPE
    tool_name: str | None = None
    quantity_given: int | None = None
    quantity_returned: int | None = None


class SessionToolRepositoryProtocol(
    RepositoryProtocol[SessionTool, SessionToolUpdateDto, SessionToolDB]
):
    async def session_tools_info(self, session_id: ID_TYPE) -> list[SessionTool]: ...


class SessionToolRepository(
    SessionToolRepositoryProtocol,
    SqlAlchemyRepository[SessionTool, SessionToolUpdateDto, SessionToolDB],
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
