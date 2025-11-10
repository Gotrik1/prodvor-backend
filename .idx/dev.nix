# .idx/dev.nix (IDX schema: channel + packages + env + idx.*)
{ pkgs, ... }:
{
  # Версию канала подправь при необходимости
  channel = "stable-24.05";

  # Инструменты, которые должны переживать пересборки среды
  packages = [    
    pkgs.git
    pkgs.bash
    pkgs.openssh
    pkgs.docker_27
    pkgs.docker-compose
    pkgs.python3
    pkgs.lsof
    pkgs.postgresql
    pkgs.redocly    
  ];

  # Глобальные переменные окружения
  env = {
    # Git всегда использует ssh из Nix
    GIT_SSH_COMMAND = "${pkgs.openssh}/bin/ssh";
  };

  # Включаем только Docker, PostgreSQL будет в нем
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
          # Запускаем Docker Compose, а затем FastAPI
          command = [ 
            "bash" 
            "-c" 
            # Используем '' для многострочного скрипта в Nix
            '''
              # 0. Ждем, пока Docker-демон запустится.
              echo "Waiting for Docker daemon to start..."
              while ! docker info > /dev/null 2>&1; do
                sleep 1
              done
              echo "Docker daemon started."

              # 1. Запускаем все сервисы из docker-compose.yml в фоновом режиме.
              #    Флаг --wait дожидается, пока healthcheck для postgres не пройдет.
              docker-compose up -d --wait

              # 2. Устанавливаем DATABASE_URL для подключения к БД в Docker.
              #    Используем учетные данные из docker-compose.yml (prodvor:prodvor@localhost:5432/prodvor)
              export DATABASE_URL="postgresql://prodvor:prodvor@localhost:5432/prodvor"

              # 3. Активируем venv и запускаем FastAPI с Uvicorn.
              source .venv/bin/activate
              echo "Запускаем FastAPI-сервер с Uvicorn..."
              exec uvicorn app.main:app --host=0.0.0.0 --port=8080 --reload
            '''
          ];
          manager = "web";
        };
      };
    };
  };
}
