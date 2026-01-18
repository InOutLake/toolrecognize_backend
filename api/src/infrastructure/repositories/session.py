from typing import Annotated, Any, Mapping, Sequence, Type
from fastapi import Depends
from sqlalchemy import Select

from sqlalchemy.orm import selectinload
from application.session.dtos import SessionUpdateDto
from infrastructure.database import Session as SessionDB, DbSessionDep
from domain.session import Session
from shared.interfaces.repository import RepositoryProtocol
from .sqlalchemy_repository import SqlAlchemyRepository
from .session_tool import SessionToolRepositoryProtocol, SessionToolRepositoryDep


class SessionRepositoryProtocol(
    RepositoryProtocol[Session, SessionUpdateDto, SessionDB]
):
    def __init__(
        self,
        domain_model: Type[Session],
        database_model: Type[SessionDB],
        session: Any,
        session_tool_repository: SessionToolRepositoryProtocol,
    ) -> None: ...


class SessionRepository(
    SqlAlchemyRepository[Session, SessionUpdateDto, SessionDB],
    SessionRepositoryProtocol,
):
    def __init__(
        self,
        domain_model: Type[Session],
        database_model: Type[SessionDB],
        session_tool_repository: SessionToolRepositoryProtocol,
        session: Any,
    ) -> None:
        self._session_tool_repository = session_tool_repository
        super().__init__(domain_model, database_model, session)

    # Added selectinload for session_tools
    def _build_select(
        self,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
        order_by: Sequence[Any] | None = None,
    ) -> Select[tuple[SessionDB]]:
        stmt = super()._build_select(filters, extra_filters, order_by)
        return stmt.options(selectinload(SessionDB.session_tools))

    async def to_orm(self, data: Sequence[Session]) -> list[SessionDB]:
        rows = []
        for session in data:
            row = SessionDB(**session.model_dump())
            row.session_tools = await self._session_tool_repository.to_orm(
                list(session.session_tools.values())
            )
            rows.append(row)
        return rows

    async def to_domain(self, data: Sequence[SessionDB]) -> list[Session]:
        sessions = []
        for row in data:
            session = Session.model_validate(row)
            session_tools = await self._session_tool_repository.session_tools_info(
                row.id
            )
            session.session_tools = {tool.id: tool for tool in session_tools}
            sessions.append(session)
        return sessions


def get_session_repository(
    db: DbSessionDep, session_tool_repository: SessionToolRepositoryDep
) -> SessionRepositoryProtocol:
    return SessionRepository(Session, SessionDB, session_tool_repository, db)


SessionRepositoryDep = Annotated[
    SessionRepositoryProtocol, Depends(get_session_repository)
]
