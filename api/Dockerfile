FROM python:3.13-slim AS base
RUN pip install uv

FROM base as deps

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv venv .venv \
    && uv sync --frozen

FROM deps AS final

WORKDIR /app
COPY . .

EXPOSE 5678 8000

CMD ["uv", "run", "main.py"]


