FROM python:3.9-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Сначала копируем только requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Затем копируем весь проект
COPY . .

# Устанавливаем PYTHONPATH
ENV PYTHONPATH="${PYTHONPATH}:/app"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]