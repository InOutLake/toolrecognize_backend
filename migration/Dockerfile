FROM python:3.13-slim as base
RUN pip install uv

FROM base as deps

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv venv .venv \
    && uv sync --frozen

FROM deps as final

WORKDIR /app
COPY . .

ENV PATH="/app/.venv/bin:$PATH"

CMD ["alembic", "upgrade", "head"]
