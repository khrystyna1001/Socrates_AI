FROM python:3.12-slim

ARG HF_TOKEN
RUN echo "${HF_TOKEN}"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    UV_PROJECT_ENVIRONMENT=/.venv \
    HF_DEBUG=1

COPY --from=ghcr.io/astral-sh/uv:0.8.14 /uv /uvx /bin/

COPY pyproject.toml uv.lock /_lock/

RUN --mount=type=cache,target=/root/.cache \
    cd /_lock && \
    uv sync \
    --frozen \
    --no-install-project

RUN uvx --from huggingface_hub hf auth login && \
    uvx --from huggingface_hub hf download "all-MiniLM-L6-v2" 

COPY . .