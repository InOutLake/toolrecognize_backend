import uvicorn
from fastapi import APIRouter, FastAPI

from src.api import (
    employee_router,
    session_router,
    tool_router,
    kit_router,
    location_router,
)

app = FastAPI(title="Tools stacktaking control app", version="0.0.1")


def include_routers(app: FastAPI, *routers: APIRouter) -> None:
    for router in routers:
        app.include_router(router)


def main():
    include_routers(
        app,
        employee_router,
        session_router,
        tool_router,
        kit_router,
        location_router,
    )
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
