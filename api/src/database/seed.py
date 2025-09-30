import asyncio

from sqlalchemy import delete
from src.database import (
    Employee,
    Tool,
    Kit,
    Storage,
    ToolInKit,
)
from .database import AsyncSessionLocal

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
        await session.execute(delete(ToolInKit))
        await session.execute(delete(Kit))
        await session.execute(delete(Tool))
        await session.execute(delete(Employee))
        await session.execute(delete(Storage))
        await session.commit()
        employees = [Employee(name=name) for name in EMPLOYEES]
        session.add_all(employees)

        location = Storage(name=LOCATION["name"], address=LOCATION["address"])
        session.add(location)

        kit = Kit(name=KIT_NAME, description="")
        session.add(kit)
        await session.flush()

        tools = []
        for tool_name in TOOL_NAMES:
            tool = Tool(name=tool_name, description="")
            session.add(tool)
            await session.flush()
            tools.append(tool)
            kit_tool = ToolInKit(tool_id=tool.id, kit_id=kit.id, quantity=1)
            session.add(kit_tool)

        await session.commit()
    print("Seed data added.")


if __name__ == "__main__":
    asyncio.run(seed())
