from typing import Annotated
from fastapi import Depends
from sqlalchemy.exc import NoResultFound

from src.core import AsyncRepository
from src.database import DbSessionDep, Kit, ID_TYPE


class KitRepository(AsyncRepository[Kit]):
    async def get_kit_tools(self, kit_id: ID_TYPE):
        kit = await self.get_one(filters={"id": kit_id})
        if kit is None:
            raise NoResultFound()
        return kit.tools_in_kit


def get_kit_repository(db: DbSessionDep) -> KitRepository:
    return KitRepository(Kit, db)


KitRepositoryDep = Annotated[KitRepository, Depends(get_kit_repository)]
