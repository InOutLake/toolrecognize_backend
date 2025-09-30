from __future__ import annotations

from typing import (
    Any,
    Generic,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    TypeVar,
)

from sqlalchemy import Select, case, delete, func, inspect, select, update
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.exc import NoResultFound

ModelT = TypeVar("ModelT", bound=DeclarativeBase)


class AsyncRepository(Generic[ModelT]):
    def __init__(self, model: Type[ModelT], session: AsyncSession) -> None:
        self.model: Type[ModelT] = model
        self.session: AsyncSession = session

    def _build_select(
        self,
        filters: Optional[Mapping[str, Any]] = None,
        extra_filters: Optional[Sequence[Any]] = None,
        order_by: Optional[Sequence[Any]] = None,
    ) -> Select[tuple[ModelT]]:
        stmt: Select[tuple[ModelT]] = select(self.model)

        if filters:
            for field_name, value in filters.items():
                if value is not None:
                    column = getattr(self.model, field_name, None)
                    if column is None:
                        raise AttributeError(
                            f"Model {self.model.__name__} has no column '{field_name}'"
                        )
                    stmt = stmt.where(column == value)

        if extra_filters:
            for expr in extra_filters:
                stmt = stmt.where(expr)

        if order_by and len(order_by) > 0:
            stmt = stmt.order_by(*order_by)
        else:
            pk_cols = inspect(self.model).primary_key
            if pk_cols:
                stmt = stmt.order_by(*pk_cols)

        return stmt

    async def list(
        self,
        *,
        filters: Optional[Mapping[str, Any]] = None,
        extra_filters: Optional[Sequence[Any]] = None,
        order_by: Optional[Sequence[Any]] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[ModelT], int]:
        base_stmt = self._build_select(
            filters=filters, extra_filters=extra_filters, order_by=order_by
        )

        count_stmt = select(func.count()).select_from(
            base_stmt.order_by(None).subquery()
        )
        count_result: Result = await self.session.execute(count_stmt)
        total: int = int(count_result.scalar_one())

        page_stmt = base_stmt.limit(limit).offset(offset)
        result: Result = await self.session.execute(page_stmt)
        items: List[ModelT] = list(result.scalars().all())
        return items, total

    async def get_one(
        self,
        *,
        filters: Optional[Mapping[str, Any]] = None,
        extra_filters: Optional[Sequence[Any]] = None,
    ) -> Optional[ModelT]:
        stmt = self._build_select(filters=filters, extra_filters=extra_filters)
        stmt = stmt.limit(1)
        result: Result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, data: Mapping[str, Any]) -> ModelT:
        obj = self.model(**dict(data))
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        await self.session.commit()
        return obj

    async def create_many(self, data: list[ModelT]) -> list[ModelT]:
        self.session.add_all(data)
        await self.session.flush()
        for row in data:
            await self.session.refresh(row)
        await self.session.commit()
        return data

    async def update(self, id_value: Any, data: Mapping[str, Any]) -> Optional[ModelT]:
        pk_cols = inspect(self.model).primary_key
        if len(pk_cols) != 1:
            raise ValueError(
                "update() supports models with a single-column primary key"
            )
        pk_col = pk_cols[0]

        upd_stmt = (
            update(self.model)
            .where(pk_col == id_value)
            .values(**dict(data))
            .returning(self.model)
        )
        result: Result = await self.session.execute(upd_stmt)
        obj = result.scalars().first()
        if obj is None:
            await self.session.rollback()
            raise NoResultFound()
        await self.session.commit()
        return obj

    async def update_many(
        self, updates: list[tuple[Any, Mapping[str, Any]]]
    ) -> list[ModelT]:
        if not updates:
            return []

        pk_cols = inspect(self.model).primary_key
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
            column = getattr(self.model, field_name, None)
            if column is None:
                raise AttributeError(
                    f"Model {self.model.__name__} has no column '{field_name}'"
                )

            case_when_clauses[field_name] = case(
                *[(pk_col == id_val, value) for id_val, value in value_map.items()],
                else_=column,
            )

        upd_stmt = (
            update(self.model)
            .where(pk_col.in_(id_values))
            .values(**case_when_clauses)
            .returning(self.model)
        )

        result = await self.session.execute(upd_stmt)
        updated_objects = list(result.scalars().all())
        await self.session.commit()
        return updated_objects

    async def delete(self, id_value: Any) -> bool:
        pk_cols = inspect(self.model).primary_key
        if len(pk_cols) != 1:
            raise ValueError(
                "delete() supports models with a single-column primary key"
            )
        pk_col = pk_cols[0]

        del_stmt = delete(self.model).where(pk_col == id_value)
        result = await self.session.execute(del_stmt)
        await self.session.commit()
        return result.rowcount is not None and result.rowcount > 0
