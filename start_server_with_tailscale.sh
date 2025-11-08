#!/bin/bash

# Запускаем Tailscale в фоновом режиме
# --socks5-server=localhost:1080 создает локальный SOCKS5 прокси
# --accept-dns=false важно, чтобы не переписывать /etc/resolv.conf в NixOS
tailscale up --socks5-server=localhost:1080 --accept-dns=false &

# Ждем немного, чтобы Tailscale успел запуститься
sleep 5

# Активируем виртуальное окружение Python
source .venv/bin/activate

# Запускаем Flask-сервер
flask run --host=0.0.0.0 --port=8080
