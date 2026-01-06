from typing import Any, Protocol, TypeVar

from pydantic import BaseModel

from application.shared.dtos import CreateDto, FiltersDto, UpdateDto
from domain.shared import DomainModelT
from shared.dtos import Page, PageParams
from .repository import RepositoryProtocol

CreateModelT = TypeVar("CreateModelT", bound=CreateDto, contravariant=True)
UpdateModelT = TypeVar("UpdateModelT", bound=UpdateDto, contravariant=True)
FiltersModelT = TypeVar("FiltersModelT", bound=FiltersDto, contravariant=True)

T = TypeVar("T", bound=BaseModel)


class CRUDServiceProtocol(
    Protocol[DomainModelT, CreateModelT, UpdateModelT, FiltersModelT]
):
    """CRUD operations service protocol. Mixin to add basic CRUD interface for domain"""

    def __init__(self, repository: RepositoryProtocol[DomainModelT, Any]) -> None: ...

    async def get_page(
        self, filters: FiltersModelT, page: PageParams
    ) -> Page[DomainModelT]: ...
    async def get_one(self, id: Any) -> DomainModelT | None: ...

    async def get_one_or_raise(self, id: Any) -> DomainModelT: ...

    async def create(
        self, data: CreateModelT | list[CreateModelT]
    ) -> list[DomainModelT]: ...

    async def update(
        self, data: UpdateModelT | list[UpdateModelT]
    ) -> list[DomainModelT]: ...

    async def delete(self, data: Any | list[Any]) -> bool: ...
