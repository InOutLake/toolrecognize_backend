from datetime import datetime
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Annotated, AsyncGenerator
from fastapi import Depends
from enum import StrEnum, auto

from src.core import SETTINGS
from src.core import ID_TYPE as id_type


ID_TYPE = Mapped[id_type]


class SessionStatus(StrEnum):
    open_waiting_for_aproval = auto()
    opened = auto()
    close_waiting_for_aproval = auto()
    closed = auto()


class TimestampMixin:
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.now(),
        nullable=False,
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Base(DeclarativeBase):
    pass


class Employee(TimestampMixin, Base):
    __tablename__ = "employee"

    id: ID_TYPE = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    reciever_sessions: Mapped[list["Session"]] = relationship(
        back_populates="reciever", foreign_keys="Session.reciever_id"
    )
    giver_sessions: Mapped[list["Session"]] = relationship(
        back_populates="giver", foreign_keys="Session.giver_id"
    )


class Tool(TimestampMixin, Base):
    __tablename__ = "tool"

    id: ID_TYPE = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(50))

    session_tools: Mapped[list["SessionTool"]] = relationship(back_populates="tool")
    tools_in_kits: Mapped[list["ToolInKit"]] = relationship(back_populates="tool")


class Session(TimestampMixin, Base):
    __tablename__ = "session"

    id: ID_TYPE = mapped_column(primary_key=True)
    reciever_id: ID_TYPE = mapped_column(ForeignKey("employee.id"))
    giver_id: ID_TYPE = mapped_column(ForeignKey("employee.id"))
    location_id: ID_TYPE = mapped_column(ForeignKey("location.id"))
    kit_id: ID_TYPE = mapped_column(ForeignKey("kit.id"))

    status: Mapped[SessionStatus] = mapped_column()

    given_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=True)
    returned_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    given_image_key: Mapped[str] = mapped_column(String(), nullable=True)
    returned_image_key: Mapped[str] = mapped_column(String(), nullable=True)

    reciever: Mapped["Employee"] = relationship(
        back_populates="reciever_sessions",
        foreign_keys=[reciever_id],
    )
    giver: Mapped["Employee"] = relationship(
        back_populates="giver_sessions",
        foreign_keys=[giver_id],
    )
    location: Mapped["Storage"] = relationship(back_populates="sessions")
    kit: Mapped["Kit"] = relationship(back_populates="sessions")
    session_tools: Mapped[list["SessionTool"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class SessionTool(TimestampMixin, Base):
    __tablename__ = "session_tool"

    id: ID_TYPE = mapped_column(primary_key=True)
    tool_id: ID_TYPE = mapped_column(ForeignKey("tool.id"))
    session_id: ID_TYPE = mapped_column(ForeignKey("session.id"))

    quantity_given: Mapped[int] = mapped_column(Integer())
    quantity_returned: Mapped[int] = mapped_column(Integer())

    tool: Mapped["Tool"] = relationship(back_populates="session_tools")
    session: Mapped["Session"] = relationship(back_populates="session_tools")

    __table_args__ = (
        CheckConstraint("quantity_given >= 0", name="check_quantity_given_positive"),
        CheckConstraint(
            "quantity_returned >= 0", name="check_quantity_returned_positive"
        ),
    )


class Kit(TimestampMixin, Base):
    __tablename__ = "kit"

    id: ID_TYPE = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(100), nullable=True)

    sessions: Mapped[list["Session"]] = relationship(back_populates="kit")
    tools_in_kit: Mapped[list["ToolInKit"]] = relationship(back_populates="kit")


class ToolInKit(TimestampMixin, Base):
    __tablename__ = "tools_in_kit"

    id: ID_TYPE = mapped_column(primary_key=True)
    tool_id: ID_TYPE = mapped_column(ForeignKey("tool.id"))
    kit_id: ID_TYPE = mapped_column(ForeignKey("kit.id"))
    quantity: Mapped[int] = mapped_column(Integer(), default=1)

    tool: Mapped["Tool"] = relationship(back_populates="tools_in_kits")
    kit: Mapped["Kit"] = relationship(back_populates="tools_in_kit")

    __table_args__ = (
        CheckConstraint("quantity > 0", name="check_kit_quantity_positive"),
    )


class Storage(TimestampMixin, Base):
    __tablename__ = "location"

    id: ID_TYPE = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))
    address: Mapped[str] = mapped_column(String(100))

    sessions: Mapped[list["Session"]] = relationship(back_populates="location")


engine = create_async_engine(
    url=SETTINGS.database_url,
    echo=False,
    future=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
