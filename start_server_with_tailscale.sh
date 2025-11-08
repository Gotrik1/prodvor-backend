#!/bin/bash

# 1. Завершаем старые процессы tailscaled для чистого старта.
pkill -f tailscaled

# 2. Запускаем демон Tailscale в фоновом режиме.
/home/user/.local/bin/tailscaled --tun=userspace-networking --socks5-server=localhost:1080 --statedir=/home/user/.tailscale/stated --socket=/home/user/.tailscale/tailscaled.sock &

# 3. Ждем, пока SOCKS5-прокси будет готов.
echo "Waiting for Tailscale SOCKS5 proxy on port 1080..."
while ! (</dev/tcp/localhost/1080) &>/dev/null; do
  sleep 1
done
echo "Tailscale SOCKS5 proxy is ready."

# 4. Поднимаем сетевой интерфейс Tailscale.
/home/user/.local/bin/tailscale --socket=/home/user/.tailscale/tailscaled.sock up --accept-routes --accept-dns=false

# 5. Активируем виртуальное окружение Python.
source .venv/bin/activate

# 6. Устанавливаем переменную окружения для Flask.
export FLASK_APP=main.py

# 7. Используем 'exec', чтобы заменить процесс скрипта на сервер Flask.
# Это делает Flask-сервер основным процессом и предотвращает завершение скрипта
# и убийство фонового процесса tailscaled.
exec python3 -m flask run --host=0.0.0.0 --port=8080
