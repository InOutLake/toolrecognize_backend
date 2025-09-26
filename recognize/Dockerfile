FROM python:3.13-slim as base
RUN pip install uv

FROM base as deps

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv venv .venv \
    && uv pip install --python .venv/bin/python -r uv.lock

FROM deps as final

WORKDIR /app
COPY . .

CMD ["python", "-X", "utf8", "main.py"]


