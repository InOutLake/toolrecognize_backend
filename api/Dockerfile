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

EXPOSE 8000

CMD ["uv", "run", "main.py"]


