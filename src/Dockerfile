FROM python:3.12-slim

WORKDIR /app

ARG HF_TOKEN

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/.venv \
    HF_DEBUG=1 \
    HF_TOKEN=${HF_TOKEN}

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/

COPY pyproject.toml uv.lock /_lock/

RUN --mount=type=cache,target=/root/.cache \
    cd /_lock && \
    uv sync \
    --frozen \
    --no-install-project

RUN uvx --from huggingface_hub hf auth login && \
    uvx --from huggingface_hub hf download sentence-transformers/all-mpnet-base-v2

RUN curl -fsSL https://ollama.com/install.sh | OLLAMA_VERSION=0.5.7 sh

    # docker exec -it ollama ollama pull tinyllama

COPY . .
