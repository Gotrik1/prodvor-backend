#!/bin/bash
# Активируем виртуальное окружение
source .venv/bin/activate

# Устанавливаем переменные для Flask
export FLASK_APP=main.py

# Запускаем Flask-сервер. 
# Переменная ALL_PROXY уже установлена в dev.nix, поэтому ее здесь не нужно указывать.
# Сервер будет доступен извне на порту 8080
python3 -m flask run --host=0.0.0.0 --port=8080
