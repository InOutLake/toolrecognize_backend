from typing import Annotated, Any, Mapping, Optional, Sequence, override
from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from src.core import AsyncRepository
from src.core import ID_TYPE
from src.database.database import (
    DbSessionDep,
    Kit,
    Session,
    SessionStatus,
    SessionTool,
    Tool,
    ToolInKit,
)


class SessionRepository(AsyncRepository[Session]):
    async def full_tools_info(self, session_id: ID_TYPE):
        stmt = (
            select(
                Session.id.label("session_id"),
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
                SessionTool,
                (SessionTool.session_id == Session.id)
                & (SessionTool.tool_id == Tool.id),
            )
            .where(Session.id == session_id)
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def open_session(self, session_id: ID_TYPE):
        await self.update(session_id, {"status": SessionStatus.opened})

    async def close_session(self, session_id: ID_TYPE):
        await self.update(session_id, {"status": SessionStatus.closed})

    @override
    async def get_one(
        self,
        *,
        filters: Optional[Mapping[str, Any]] = None,
        extra_filters: Optional[Sequence[Any]] = None,
    ) -> Session | None:
        stmt = self._build_select(filters=filters, extra_filters=extra_filters).options(
            selectinload(Session.session_tools)
        )
        stmt = stmt.limit(1)
        result = await self.session.execute(stmt)
        return result.scalars().first()


def get_session_repository(db: DbSessionDep) -> SessionRepository:
    return SessionRepository(Session, db)


SessionRepositoryDep = Annotated[SessionRepository, Depends(get_session_repository)]
