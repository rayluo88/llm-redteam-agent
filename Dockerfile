FROM python:3.13-slim

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

COPY src/ ./src/
COPY scripts/ ./scripts/

CMD ["uv", "run", "python", "scripts/run_eval.py"]
