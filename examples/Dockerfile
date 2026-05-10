FROM mcr.microsoft.com/playwright/python:v1.59.0-noble

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --no-dev

# arm64 Linux では Chromium のみサポート (Firefox は arm64 非対応)
RUN uv run playwright install chromium --with-deps

COPY main.py .

CMD ["uv", "run", "python", "main.py"]
