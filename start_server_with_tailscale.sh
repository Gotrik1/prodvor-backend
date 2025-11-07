#!/bin/bash

# 0. Завершаем старые процессы tailscaled, если они есть
pkill -f tailscaled

# 1. Запускаем демон Tailscale в фоновом режиме
/home/user/.local/bin/tailscaled --tun=userspace-networking --socks5-server=localhost:1080 --statedir=/home/user/.tailscale/stated --socket=/home/user/.tailscale/tailscaled.sock & 

# 2. Ждем, пока он запустится
sleep 5 

# 3. Поднимаем сетевой интерфейс Tailscale
/home/user/.local/bin/tailscale --socket=/home/user/.tailscale/tailscaled.sock up --accept-routes --accept-dns=false

# 4. Запускаем наш основной скрипт сервера
./devserver.sh
