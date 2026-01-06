from typing import Annotated, Callable, Generic, Type

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from application.service import CRUDService
from application.shared.dtos import (
    CreateModelT,
    FiltersModelT,
    ResponseModelT,
    UpdateBaseModelT,
    UpdateModelT,
)
from domain.shared import ID_TYPE, DomainModelT
from infrastructure.repositories.sqlalchemy_repository import (
    SqlAlchemyModelT,
    SqlAlchemyRepository,
)
from shared.dtos.page import Page, PageRequestDep


class CRUDRouterFactory(
    Generic[
        DomainModelT,
        SqlAlchemyModelT,
        CreateModelT,
        UpdateModelT,
        UpdateBaseModelT,
        FiltersModelT,
        ResponseModelT,
    ]
):
    """
    This one was a humble attempt to get rid of boilerplate CRUD api code.
    Of course it did not work, fastapi doesn't work with generics.
    I shall research on other Python mechanisms that may allow achieve my idea.
    Maybe a simple inheritance, or even a function with parametrized types could do.
    """

    def __init__(
        self,
        entity_name: str,
        domain_model: Type[DomainModelT],
        sqlalchemy_model: Type[SqlAlchemyModelT],
        db_session: AsyncSession,
        create_model: Type[CreateModelT],
        update_model: Type[UpdateModelT],
        filters_model: Type[FiltersModelT],
        filters_dep: Callable[..., FiltersModelT],
        response_model: Type[ResponseModelT],
    ):
        self.entity_name = entity_name
        self.update_model = update_model
        self.domain_model = domain_model
        self.sqlalchemy_model = sqlalchemy_model
        self.response_model = response_model
        self.filters_dep = filters_dep

        class EntityRepository(
            SqlAlchemyRepository[domain_model, sqlalchemy_model]
        ): ...

        class EntityService(
            CRUDService[domain_model, create_model, update_model, filters_model]
        ): ...

        repository = EntityRepository(domain_model, sqlalchemy_model, db_session)
        self._service = EntityService(domain_model, repository)

        self.router = APIRouter(prefix=f"/{entity_name}", tags=[entity_name])

        @self.router.get("/")
        def test(data: Annotated[filters_model, Body(...)]): ...

        self._add_routes()

    def _add_routes(self):
        @self.router.get("/", response_model=Page[self.response_model])
        async def list_entities(
            page: PageRequestDep,
            filters: Annotated[
                FiltersModelT,
                Depends(self.filters_dep),
            ],
        ) -> Page[DomainModelT]:
            return await self._service.get_page(filters, page)

        @self.router.post("/", response_model=self.response_model)
        async def create_entity(data: CreateModelT = Body(...)) -> DomainModelT:
            return (await self._service.create(data))[0]

        @self.router.get("/{entity_id}", response_model=self.response_model)
        async def get_entity_details(entity_id: ID_TYPE) -> DomainModelT:
            return await self._service.get_one_or_raise(entity_id)

        @self.router.put("/{entity_id}", response_model=self.response_model)
        async def update_entity(
            entity_id: ID_TYPE,
            data: UpdateBaseModelT = Body(...),
        ) -> list[DomainModelT]:
            return await self._service.update(
                [self.update_model(id=entity_id, **data.model_dump())]
            )

        @self.router.delete("/{entity_id}")
        async def delete_entity(entity_id: ID_TYPE) -> bool:
            return await self._service.delete(entity_id)
