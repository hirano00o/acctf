FROM mcr.microsoft.com/playwright/python:v1.59.0-noble

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

# arm64 Linux では Chromium のみサポート (Firefox は arm64 非対応)
RUN uv run playwright install chromium --with-deps

COPY . .
RUN uv sync --frozen --no-dev

CMD ["uv", "run", "python"]
