from typing import Annotated
from fastapi import Depends
from src.core import AsyncRepository
from src.database import DbSessionDep, Storage


class LocationRepository(AsyncRepository[Storage]):
    pass


def get_location_repository(db: DbSessionDep) -> LocationRepository:
    return LocationRepository(Storage, db)


LocationRepositoryDep = Annotated[LocationRepository, Depends(get_location_repository)]
