FROM nvidia/cuda:13.1.0-runtime-ubuntu24.04 AS base

RUN apt-get update && apt-get install -y \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN uv python install 3.13
RUN uv python pin 3.13
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv venv .venv \
    && uv sync --frozen

FROM base
WORKDIR /app
COPY . .
CMD ["uv", "run", "main.py"]
