from typing import Annotated, Callable, Type, Any

from fastapi import APIRouter, Body, Depends, HTTPException, status

from application.service import CRUDService
from application.shared.dtos import (
    CreateDto,
    FiltersDto,
    ResponseDto,
    UpdateDtoBase,
    UpdateDto,
)
from domain.shared import ID_TYPE, Domain
from infrastructure.database.database import DbSessionDep
from infrastructure.repositories.sqlalchemy_repository import (
    SqlAlchemyRepository,
)
from shared.dtos.page import Page, PageRequestDep
from infrastructure.database import Base


"""
This is the only hard dependecy from the infrastructure layer here.
It is absolutely viable to manage routes without hard deps.
Look src/presentation/api/employee as an example.
I simply couldn't bother writing tons of boilerplate code for basic CRUD operations.
Generics were not an option here due to the way fastapi works and the way 
Python resolves them (generics).
There is also another viable option: fastapi-crudrouter library, which provides basically the same 
functionality. But I discovered it a bit too late :'D
"""


def crud_router_factory(
    entity_name: str,
    domain_model: Type[Domain],
    sqlalchemy_model: Type[Base],
    create_model: Type[CreateDto],
    update_base: Type[UpdateDtoBase],
    update_model: Type[UpdateDto],
    filters_model: Type[FiltersDto],
    filters_func: Callable[..., FiltersDto],
    response_model: Type[ResponseDto],
) -> APIRouter:
    router = APIRouter(prefix=f"/{entity_name}", tags=[entity_name])

    async def get_service(session: DbSessionDep):
        repo = SqlAlchemyRepository(domain_model, sqlalchemy_model, session)
        return CRUDService(domain_model, update_model, repo)

    # --- read ---
    async def list_entities(
        service: Annotated[Any, Depends(get_service)],
        page: PageRequestDep,
        filters: Any,
    ):
        return await service.get_page(filters, page)

    # NOTE: A little trick with annotations for FastAPI.
    list_entities.__annotations__["filters"] = Annotated[
        filters_model, Depends(filters_func)
    ]
    router.add_api_route(
        "", list_entities, methods=["GET"], response_model=Page[response_model]
    )

    @router.get("/{entity_id}", response_model=response_model)
    async def get_by_id(
        service: Annotated[Any, Depends(get_service)], entity_id: ID_TYPE
    ):
        entity = await service.get_by_id(entity_id)
        if entity is None:
            raise HTTPException(status_code=404, detail="Entity not found")
        return entity

    # --- create ---
    async def create_entity(service: Annotated[Any, Depends(get_service)], data: Any):
        return await service.create(data)

    create_entity.__annotations__["data"] = Annotated[list[create_model], Body(...)]
    router.add_api_route(
        "", create_entity, methods=["POST"], response_model=list[response_model]
    )

    # --- update ---
    # TODO: this should support bulk operations too
    async def update_entity(
        service: Annotated[Any, Depends(get_service)],
        entity_id: ID_TYPE,
        data: Any,
    ):
        result = await service.update(
            update_model(id=entity_id, **data.model_dump(exclude_unset=True))
        )
        return result[0]

    update_entity.__annotations__["data"] = Annotated[update_base, Body(...)]
    router.add_api_route(
        "/{entity_id}", update_entity, response_model=response_model, methods=["PUT"]
    )

    # --- delete ---
    @router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_entity(
        service: Annotated[Any, Depends(get_service)], entity_id: ID_TYPE
    ) -> None:
        result = await service.delete(entity_id)
        if result:
            return None
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    return router
