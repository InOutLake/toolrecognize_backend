import asyncio

from sqlalchemy import delete, select
from src.database import (
    Employee,
    Tool,
    Kit,
    Storage,
    ToolInKit,
)
from .database import AsyncSessionLocal, Session

KIT_NAME = "ОНИ для ЦОТО УФ RRJ/737/32S"
TOOL_NAMES = [
    "Коловорот",
    "Шерница",
    "Бокорезы",
    "Разводной ключ",
    "Отвертка +",
    "Отвертка на смещенный крест",
    "Пассатижи контровочные",
    "Ключ 3/4",
    "Отвертка -",
    "Открывашка для банок с маслом",
    "Пассатижи",
]
EMPLOYEES = ["Иван Иванов", "Петр Петров", "Мария Смирнова"]
LOCATION = {"name": "ЦОТО УФ RRJ/737/32S", "address": "Москва, ул. Примерная, 1"}


async def seed():
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Employee))
        if not result.scalars().first():
            employees = [Employee(name=name) for name in EMPLOYEES]
            session.add_all(employees)

        result = await session.execute(
            select(Storage).where(Storage.name == LOCATION["name"])
        )
        location = result.scalar_one_or_none()
        if not location:
            location = Storage(name=LOCATION["name"], address=LOCATION["address"])
            session.add(location)
            await session.flush()

        result = await session.execute(select(Kit).where(Kit.name == KIT_NAME))
        kit = result.scalar_one_or_none()
        if not kit:
            kit = Kit(name=KIT_NAME, description="")
            session.add(kit)
            await session.flush()

        existing_tools = await session.execute(select(Tool))
        existing_names = {t.name for t in existing_tools.scalars()}
        new_tools = []

        for tool_name in TOOL_NAMES:
            if tool_name not in existing_names:
                tool = Tool(name=tool_name, description="")
                session.add(tool)
                new_tools.append(tool)

        await session.flush()

        if new_tools or kit:
            stmt = select(ToolInKit.tool_id).where(ToolInKit.kit_id == kit.id)
            existing_tool_ids = set((await session.execute(stmt)).scalars().all())

            all_tools = await session.execute(select(Tool))
            all_tool_map = {t.name: t.id for t in all_tools.scalars()}

            for name in TOOL_NAMES:
                tool_id = all_tool_map[name]
                if tool_id not in existing_tool_ids:
                    kit_tool = ToolInKit(tool_id=tool_id, kit_id=kit.id, quantity=1)
                    session.add(kit_tool)

        await session.commit()
    print("Seed data added.")


if __name__ == "__main__":
    asyncio.run(seed())
