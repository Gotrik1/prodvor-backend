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
    pkgs.inotify-tools
    pkgs.entr
    pkgs.python3
    pkgs.lsof
    pkgs.postgresql      # ← тут psql
    pkgs.tailscale     # Устанавливаем Tailscale
  ];

  # Глобальные переменные окружения
  env = {
    # Git всегда использует ssh из Nix
    GIT_SSH_COMMAND = "${pkgs.openssh}/bin/ssh";
    # Добавляем прокси для Tailscale
    ALL_PROXY = "socks5://localhost:1080/";
  };

  # Включаем сервисы
  services.docker.enable = true;
  services.postgres.enable = true;

  # IDX-интеграции
  idx = {
    extensions = [
      "ms-python.python"
    ];

    previews = {
      enable = true;
      previews = {
        web = {
          # Запускаем через наш новый скрипт, который поднимает Tailscale
          command = [ "bash" "./start_server_with_tailscale.sh" ];
          manager = "web";
        };
      };
    };
  };
}
