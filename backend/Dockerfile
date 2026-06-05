FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock* ./

RUN poetry config repositories.aliyun https://mirrors.aliyun.com/pypi/simple/
RUN poetry config virtualenvs.create false

ENV POETRY_HTTP_TIMEOUT=600
RUN poetry install --no-interaction --no-ansi --no-root

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]