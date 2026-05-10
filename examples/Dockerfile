FROM mcr.microsoft.com/playwright/python:v1.59.0-noble

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml ./

# pyproject.toml の dependencies を venv にインストール
RUN uv venv && \
    uv pip install --python .venv/bin/python --no-cache-dir --requirement pyproject.toml

# arm64 Linux では Chromium のみサポート (Firefox は arm64 非対応)
RUN .venv/bin/python -m playwright install chromium --with-deps

COPY main.py .

CMD [".venv/bin/python", "main.py"]
