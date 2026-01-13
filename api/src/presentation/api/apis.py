from presentation.api.crud_api import crud_router_factory
from domain.storage import Storage as StorageD
from infrastructure.database.database import Storage, DbSessionDep, get_db
from application.storage.dtos import (
    StorageCreateDto,
    StorageFilters,
    StorageFiltersDep,
    StorageResponse,
    StorageUpdateDto,
    StorageUpdateDtoBase,
    storage_filters,
)

storage_router = crud_router_factory(
    "storage",
    StorageD,
    Storage,
    StorageCreateDto,
    StorageUpdateDtoBase,
    StorageUpdateDto,
    StorageFilters,
    storage_filters,
    StorageResponse,
)
