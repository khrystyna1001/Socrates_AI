FROM python:3.12-slim

WORKDIR /app

ARG HF_TOKEN
ARG MODEL_NAME=deepseek-r1:latest

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/.venv \
    HF_DEBUG=1 \
    HF_TOKEN=${HF_TOKEN} \
    OLLAMA_KEEP_ALIVE=-1 \
    OLLAMA_MODELS=/ollama/models

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/

COPY pyproject.toml uv.lock /_lock/

RUN --mount=type=cache,target=/root/.cache \
    cd /_lock && \
    uv sync \
    --frozen \
    --no-install-project

RUN uvx --from huggingface_hub hf auth login && \
    uvx --from huggingface_hub hf download sentence-transformers/all-MiniLM-L6-v2


RUN apt-get update && apt-get install -y curl ca-certificates zstd && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://ollama.com/install.sh | sh

RUN ollama serve & sleep 5 && ollama pull $MODEL_NAME

COPY . .
