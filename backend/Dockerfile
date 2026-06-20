FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

ENV UV_CACHE_DIR=/root/.cache/uv
ENV PIP_EXTRA_INDEX_URL=https://download.pytorch.org/whl/cpu
ENV UV_SYSTEM_PYTHON=1

COPY pyproject.toml uv.lock ./

RUN uv pip install --system --no-cache -e .[ai]
RUN pip install "uvicorn[standard]" websockets

COPY . .

# Проверка
RUN python -c "from faster_whisper import WhisperModel; print('✓ faster_whisper installed')"

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]