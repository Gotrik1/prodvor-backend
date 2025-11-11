# .idx/dev.nix (IDX schema: channel + packages + env + idx.*)
{ pkgs, ... }:
{
  # Канал можно оставить как есть
  channel = "stable-24.05";

  # Инструменты, которые должны переживать пересборки среды
  packages = [
    pkgs.git
    pkgs.bash
    pkgs.openssh
    pkgs.docker_27
    pkgs.docker-compose
    pkgs.inotify-tools
    pkgs.entr
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.lsof
    pkgs.postgresql
    pkgs.redocly
    pkgs.supabase-cli
  ];

  # Глобальные переменные окружения
  env = {
    # Git всегда использует ssh из Nix
    GIT_SSH_COMMAND = "${pkgs.openssh}/bin/ssh";
    # В IDX/Firebase Studio докер-демон обычно висит на /tmp/docker.sock
    DOCKER_HOST = "unix:///tmp/docker.sock";
  };

  # Включаем Docker (если поддерживается этим рантаймом)
  services.docker.enable = true;

  # IDX-интеграции
  idx = {
    extensions = [
      "ms-python.python"
    ];

    previews = {
      enable = true;
      previews = {
        web = {
          command = [
            "bash"
            "-c"
            ''
              set -euo pipefail

              echo "Waiting for Docker daemon to start..."
              # Ждём, пока docker начнёт отвечать
              until docker info >/dev/null 2>&1; do
                sleep 1
              done
              echo "Docker daemon started."

              echo "Starting docker compose services..."
              # Фоллбек на v2/v1 синтаксис
              if command -v docker >/dev/null 2>&1 && docker compose version >/dev/null 2>&1; then
                docker compose up -d --wait || docker compose up -d
              else
                docker-compose up -d --wait || docker-compose up -d
              fi

              # Жёстко вычищаем внешний DATABASE_URL и проставляем asyncpg
              unset DATABASE_URL || true
              export DATABASE_URL='postgresql+asyncpg://postgres:postgres@127.0.0.1:54322/postgres'

              # Активируем/создаём venv
              if [ ! -d ".venv" ]; then
                echo "Creating virtualenv..."
                python3 -m venv .venv
              fi
              source .venv/bin/activate

              # Обновляем pip и зависимости (тихо, чтобы не засорять лог)
              python -m pip install --upgrade pip >/dev/null
              if [ -f requirements.txt ]; then
                pip install -r requirements.txt >/dev/null
              fi

              echo "Запускаем FastAPI-сервер с Uvicorn..."
              exec uvicorn app.main:app --host=0.0.0.0 --port=8080 --reload
            ''
          ];
          manager = "web";
        };
      };
    };
  };
}
