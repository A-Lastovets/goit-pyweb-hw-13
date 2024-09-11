# Використовуємо образ Python
FROM python:3.12.2-bookworm

# Встановлюємо робочу директорію всередині контейнера
WORKDIR /app

# Копіюємо файли проекту в контейнер
COPY . /app

# Встановлюємо залежності
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Вказуємо команду для запуску FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
