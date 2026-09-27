FROM python:3.13-alpine
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_NO_DEV=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app/src"

WORKDIR /app
RUN adduser -D -u 1000 appuser && chown -R appuser:appuser /app

RUN apk add --no-cache git ffmpeg imagemagick opus deno gcc musl-dev 

COPY pyproject.toml uv.lock .
RUN uv sync --upgrade-package yt-dlp

COPY src /app/src
COPY test /app/test
USER appuser
CMD ["uv", "run", "src/app.py"]
