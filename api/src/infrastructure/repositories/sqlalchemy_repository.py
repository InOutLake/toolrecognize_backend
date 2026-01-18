from typing import (
    Any,
    Mapping,
    Sequence,
    Type,
    TypeVar,
)

from sqlalchemy import (
    Select,
    String,
    bindparam,
    func,
    insert,
    inspect,
    select,
    delete,
    update,
)
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession

from application.shared.dtos import UpdateModelT
from domain.shared import DomainModelT
from infrastructure.database import Base
from shared.dtos import Page, PageParams
from shared.interfaces.repository import RepositoryProtocol

DatabaseModelT = TypeVar("DatabaseModelT", bound=Any)


SqlAlchemyModelT = TypeVar("SqlAlchemyModelT", bound=Base)


class SqlAlchemyRepository(
    RepositoryProtocol[DomainModelT, UpdateModelT, SqlAlchemyModelT]
):
    """
    Basic CRUD operationss with async sqlalchemy library, fit for small daily operations.
    May be slow for large batches due to heavy ORM dependence.
    If performance becomes an issue create lower level repository utilizing
    `insert()` and other functions (or even asyncpg) directly.
    """

    def __init__(
        self,
        domain_model: Type[DomainModelT],
        database_model: Type[SqlAlchemyModelT],
        session: AsyncSession,
    ) -> None:
        self.domain_model = domain_model
        self.database_model = database_model
        self.session: AsyncSession = session

    async def to_orm(self, data: Sequence[DomainModelT]) -> list[SqlAlchemyModelT]:
        """Redefine for nested relations"""
        return [self.database_model(**entity.model_dump()) for entity in data]

    async def to_domain(self, data: Sequence[SqlAlchemyModelT]) -> list[DomainModelT]:
        return [self.domain_model.model_validate(m) for m in data]

    def _build_select(
        self,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
        order_by: Sequence[Any] | None = None,
    ) -> Select[tuple[SqlAlchemyModelT]]:
        """
        All the types besides `string` in filters are being compared with `equal` query.
        Strings filters applied with `lilike` query.
        """
        stmt: Select[tuple[SqlAlchemyModelT]] = select(self.database_model)

        if filters:
            for field_name, value in filters.items():
                if value is None:
                    continue

                column = getattr(self.database_model, field_name, None)
                if column is None:
                    raise AttributeError(
                        f"Model {self.database_model.__name__} has no column '{field_name}'"
                    )

                column_type = getattr(column, "type", None)
                is_string_col = column_type is not None and isinstance(
                    column_type, String
                )

                if is_string_col and isinstance(value, str):
                    stmt = stmt.where(column.ilike(f"%{value}%"))
                else:
                    stmt = stmt.where(column == value)

        if extra_filters:
            for expr in extra_filters:
                stmt = stmt.where(expr)

        if order_by and len(order_by) > 0:
            stmt = stmt.order_by(*order_by)
        else:
            pk_cols = inspect(self.database_model).primary_key
            if pk_cols:
                stmt = stmt.order_by(*pk_cols)

        return stmt

    async def get_page(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
        order_by: Sequence[Any] | None = None,
        page: PageParams,
    ) -> Page[DomainModelT]:
        """Extra filters functionality is not implemented"""
        base_stmt = self._build_select(
            filters=filters, extra_filters=extra_filters, order_by=order_by
        )

        count_stmt = select(func.count()).select_from(
            base_stmt.order_by(None).subquery()
        )
        count_result: Result = await self.session.execute(count_stmt)
        total: int = int(count_result.scalar_one())

        page_stmt = base_stmt.limit(page.page_size).offset(page.offset)
        result = await self.session.execute(page_stmt)
        rows = list(result.scalars().all())
        items = await self.to_domain(rows)
        return Page(items=items, total=total, **page.model_dump())

    async def get_one(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
    ) -> DomainModelT | None:
        page = await self.get_page(
            filters=filters,
            extra_filters=extra_filters,
            page=PageParams(page_number=1, page_size=1),
        )
        if page.items:
            return page.items[0]
        return None

    async def create(self, data: Sequence[DomainModelT]) -> list[DomainModelT]:
        rows = [m.model_dump() for m in data]
        created = await self.session.scalars(
            insert(self.database_model).returning(self.database_model), rows
        )
        await self.session.commit()
        return await self.to_domain(created.all())

    async def update(self, data: Sequence[UpdateModelT]) -> list[DomainModelT]:
        updated_entities = []
        # NOTE: it fits but it is not optimised for bulk updates. I went with this option
        # because there is no other way to support updates of non-unified data.
        for m in data:
            payload = m.model_dump(exclude_unset=True)
            stmt = (
                update(self.database_model)
                .where(self.database_model.id == m.id)
                .values(**payload)
                .returning(self.database_model)
                .execution_options(synchronize_session=False)
            )
            res = await self.session.execute(stmt)
            updated_entities.append(res.scalar_one())

        await self.session.commit()
        return await self.to_domain(updated_entities)

    async def delete(self, ids: list[Any]) -> bool:
        pk_cols = inspect(self.database_model).primary_key
        if len(pk_cols) != 1:
            raise ValueError(
                "delete() supports models with a single-column primary key"
            )
        pk_col = pk_cols[0]

        del_stmt = delete(self.database_model).where(pk_col.in_(ids))
        result = await self.session.execute(del_stmt)
        await self.session.commit()
        return result.rowcount is not None and result.rowcount > 0
