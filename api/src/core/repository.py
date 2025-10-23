from __future__ import annotations

from typing import (
    Any,
    Generic,
    List,
    Mapping,
    Optional,
    Protocol,
    Sequence,
    Type,
    TypeVar,
)

from sqlalchemy import Select, String, case, delete, func, inspect, select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase

from .schemes import Page, PageParams
from .domain import DomainModelT

DatabaseModel = TypeVar("DatabaseModel", bound=Any, covariant=True)


class AsyncRepositoryProtocol(Protocol[DomainModelT, DatabaseModel]):
    """Basic CRUD operations for database"""

    def __init__(
        self,
        domain_model: Type[DomainModelT],
        database_model: Type[DatabaseModel],
        session: Any,
    ) -> None: ...

    async def get_list(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
        order_by: Sequence[Any] | None = None,
        page: PageParams,
    ) -> Page[DomainModelT]: ...

    async def create(self, data: list[Mapping[str, Any]]) -> list[DomainModelT]: ...

    async def get_one(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
    ) -> DomainModelT | None: ...

    async def update(
        self,
        updates: list[tuple[Any, Mapping[str, Any]]],
    ) -> list[DomainModelT]: ...

    async def delete(self, ids: list[Any]) -> bool: ...


SqlAlchemyModel = TypeVar("SqlAlchemyModel", bound=DeclarativeBase, covariant=True)


class AsyncAlchemyRepository(AsyncRepositoryProtocol[DomainModelT, SqlAlchemyModel]):
    """Basic CRUD operationss utilizing async sqlalchemy library"""

    def __init__(
        self,
        domain_model: Type[DomainModelT],
        database_model: Type[SqlAlchemyModel],
        session: AsyncSession,
    ) -> None:
        self.database_model: Type[SqlAlchemyModel] = database_model
        self.domain_model: Type[DomainModelT] = domain_model
        self.session: AsyncSession = session

    def _build_select(
        self,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
        order_by: Sequence[Any] | None = None,
    ) -> Select[tuple[SqlAlchemyModel]]:
        """
        All the types besides `string` in filters are being compared with `equal` query.
        Strings filters applied with `lilike` query.
        """
        stmt: Select[tuple[SqlAlchemyModel]] = select(self.database_model)

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

    async def get_list(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
        order_by: Sequence[Any] | None = None,
        page: PageParams,
    ) -> Page[DomainModelT]:
        """Extra filters and order_by functionality is not implemented"""
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
        rows: List[SqlAlchemyModel] = list(result.scalars().all())
        items: List[DomainModelT] = list(
            [self.domain_model.model_validate(row) for row in rows]
        )
        return Page(items=items, total=total, **page.model_dump())

    async def get_one(
        self,
        *,
        filters: Mapping[str, Any] | None = None,
        extra_filters: Sequence[Any] | None = None,
    ) -> DomainModelT | None:
        page = await self.get_list(
            filters=filters,
            extra_filters=extra_filters,
            page=PageParams(page_number=1, page_size=1),
        )
        if page.items:
            return page.items[0]
        return None

    async def create(self, data: list[Mapping[str, Any]]) -> list[DomainModelT]:
        db_objects = [self.database_model(**item) for item in data]
        self.session.add_all(db_objects)
        await self.session.flush()
        for obj in db_objects:
            await self.session.refresh(obj)
        await self.session.commit()
        return [self.domain_model.model_validate(obj) for obj in db_objects]

    async def update(
        self,
        updates: list[tuple[Any, Mapping[str, Any]]],
    ) -> list[DomainModelT]:
        if not updates:
            return []

        pk_cols = inspect(self.database_model).primary_key
        if len(pk_cols) != 1:
            raise ValueError(
                "update_many() supports models with a single-column primary key"
            )
        pk_col = pk_cols[0]

        case_expressions = {}
        id_values = []

        for id_value, data in updates:
            id_values.append(id_value)
            for field_name, value in data.items():
                if field_name not in case_expressions:
                    case_expressions[field_name] = {}
                case_expressions[field_name][id_value] = value

        case_when_clauses = {}
        for field_name, value_map in case_expressions.items():
            column = getattr(self.database_model, field_name, None)
            if column is None:
                raise AttributeError(
                    f"Model {self.database_model.__name__} has no column '{field_name}'"
                )

            case_when_clauses[field_name] = case(
                *[(pk_col == id_val, value) for id_val, value in value_map.items()],
                else_=column,
            )

        upd_stmt = (
            update(self.database_model)
            .where(pk_col.in_(id_values))
            .values(**case_when_clauses)
            .returning(self.database_model)
        )

        result = await self.session.execute(upd_stmt)
        updated_objects = list(result.scalars().all())
        await self.session.commit()
        return [self.domain_model.model_validate(row) for row in updated_objects]

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
