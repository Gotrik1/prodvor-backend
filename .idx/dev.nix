{ pkgs, ... }: {
        # Канал пакетов Nix, который будет использоваться.
        channel = "stable-23.11";
        # Пакеты, необходимые для вашего проекта.
        packages = [
          pkgs.bash # Убедимся, что bash доступен для запуска скриптов
          pkgs.python3 # Явно добавляем Python 3 в окружение
          pkgs.lsof # Добавляем lsof для проверки портов, если понадобится
        ];
        # Расширения VS Code, которые будут установлены в рабочем пространстве.
        idx.extensions = [
          "ms-python.python"
        ];
        # Включаем и настраиваем предварительный просмотр.
        idx.previews = {
          enable = true;
          previews = {
            # Название нашего предпросмотра: "web"
            web = {
              # Прямая команда для запуска сервера
              command = [
                "bash"
                "-c"
                "source .venv/bin/activate && python main.py"
              ];
              manager = "web";
            };
          };
        };
      }