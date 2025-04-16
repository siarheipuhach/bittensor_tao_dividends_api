FROM python:3.11-slim

WORKDIR /app

COPY pypriject.toml ./
COPY uv.lock ./
RUN pip install uv && uv pip install --system

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
