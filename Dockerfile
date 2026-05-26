FROM python:3.11-slim

RUN pip install poetry

WORKDIR /app

COPY pyproject.toml poetry.lock* ./

RUN poetry config repositories.aliyun https://mirrors.aliyun.com/pypi/simple/
RUN poetry config virtualenvs.create false

RUN poetry config virtualenvs.create false

RUN poetry install --no-interaction --no-ansi --no-root

COPY . .


CMD ["python", "main.py"]