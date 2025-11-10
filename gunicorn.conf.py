import multiprocessing

# Количество воркеров. Рекомендуется (2 * CPU) + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Адрес и порт, на котором будет работать Gunicorn
bind = "0.0.0.0:8000"

# Класс воркера для асинхронных приложений
worker_class = "uvicorn.workers.UvicornWorker"
