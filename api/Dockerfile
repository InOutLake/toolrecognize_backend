FROM ghcr.io/astral-sh/uv:python3.13-alpine as deps
WORKDIR /app
COPY pyproject.toml uv.lock .
RUN uv venv .venv && uv sync

FROM deps AS final
WORKDIR /app
COPY . .
EXPOSE 5678
EXPOSE 8000
CMD ["uv", "run", "src/main.py"]


