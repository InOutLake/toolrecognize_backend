from typing import (
    Any,
    Mapping,
    Protocol,
    Sequence,
    Type,
    TypeVar,
)

from pydantic import BaseModel

from domain.shared import DomainModelT
from shared.dtos.page import Page, PageParams

DatabaseModelT = TypeVar("DatabaseModelT", bound=Any)


class RepositoryProtocol(Protocol[DomainModelT, DatabaseModelT]):
    """Basic CRUD operations for database"""

    def __init__(
        self,
        domain_model: Type[DomainModelT],
        database_model: Type[DatabaseModelT],
        session: Any,
    ) -> None: ...

    async def to_orm(self, data: list[BaseModel]) -> list[DatabaseModelT]: ...

    async def to_domain(self, data: list[DatabaseModelT]) -> list[DomainModelT]: ...

    async def get_page(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
        order_by: Sequence[Any] | None = None,
        page: PageParams,
    ) -> Page[DomainModelT]: ...

    async def save(self, data: list[DomainModelT]) -> list[DomainModelT]: ...

    async def get_one(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
    ) -> DomainModelT | None: ...

    async def delete(self, ids: list[Any]) -> bool: ...
