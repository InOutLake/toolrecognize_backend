FROM nvidia/cuda:12.4.0-devel-ubuntu22.04 AS base

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-venv \
    libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --upgrade pip uv

FROM base AS deps
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN python3 -m uv venv .venv \
    && python3 -m uv sync --frozen

FROM deps
WORKDIR /app
COPY . .
CMD ["uv", "run", "main.py"]
