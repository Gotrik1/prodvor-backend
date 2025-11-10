# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код приложения
COPY . .

# Запускаем приложение с помощью Gunicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-c", "gunicorn.conf.py", "app.main:app"]
