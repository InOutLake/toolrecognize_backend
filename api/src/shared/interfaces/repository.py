from typing import (
    Any,
    Mapping,
    Protocol,
    Sequence,
    Type,
    TypeVar,
)

from application.shared.dtos import UpdateModelT
from domain.shared import DomainModelT
from shared.dtos.page import Page, PageParams

DatabaseModelT = TypeVar("DatabaseModelT", bound=Any)


class RepositoryProtocol(Protocol[DomainModelT, UpdateModelT, DatabaseModelT]):
    """Basic CRUD operations for database"""

    def __init__(
        self,
        domain_model: Type[DomainModelT],
        database_model: Type[DatabaseModelT],
        session: Any,
    ) -> None: ...

    async def to_orm(self, data: Sequence[DomainModelT]) -> list[DatabaseModelT]: ...

    async def to_domain(self, data: Sequence[DatabaseModelT]) -> list[DomainModelT]: ...

    async def get_page(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
        order_by: Sequence[Any] | None = None,
        page: PageParams,
    ) -> Page[DomainModelT]: ...

    async def create(self, data: Sequence[DomainModelT]) -> list[DomainModelT]: ...

    async def update(self, data: Sequence[UpdateModelT]) -> list[DomainModelT]: ...

    async def get_one(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
    ) -> DomainModelT | None: ...

    async def delete(self, ids: list[Any]) -> bool: ...
