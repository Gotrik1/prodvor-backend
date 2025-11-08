#!/bin/bash

# Загружаем переменные окружения из .env файла
# Это позволит нам использовать TAILSCALE_AUTH_KEY
if [ -f .env ]; then
  export $(cat .env | sed 's/#.*//' | xargs)
fi

# Проверяем, есть ли ключ аутентификации
if [ -z "$TAILSCALE_AUTH_KEY" ]; then
  echo "Ошибка: Переменная TAILSCALE_AUTH_KEY не установлена в .env файле."
  echo "Пожалуйста, сгенерируйте эфемерный ключ в админ-панели Tailscale и добавьте его."
  exit 1
fi

# Запускаем Tailscale в фоновом режиме с ключом аутентификации
# --accept-routes позволяет использовать маршруты, анонсированные другими машинами (вашим home-pc)
tailscale up \
  --authkey="$TAILSCALE_AUTH_KEY" \
  --socks5-server=localhost:1080 \
  --accept-dns=false \
  --accept-routes=true &

# Ждем немного, чтобы Tailscale успел запуститься и подключиться
sleep 5

# Активируем виртуальное окружение Python
source .venv/bin/activate

# Запускаем Flask-сервер
echo "Запускаем Flask-сервер..."
flask run --host=0.0.0.0 --port=8080
