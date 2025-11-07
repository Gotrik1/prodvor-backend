# .idx/dev.nix (IDX schema: channel + packages + env + idx.*)
{ pkgs, ... }:
{
  # Версию канала подправь при необходимости
  channel = "stable-24.05";

  # Инструменты, которые должны переживать пересборки среды
  packages = [
    pkgs.python3
    pkgs.bash
    pkgs.lsof
    pkgs.git
    pkgs.openssh        # ssh, ssh-agent, ssh-add
    pkgs.inotify-tools  # inotifywait
    pkgs.entr           # альтернатива вотчеру
  ];

  # Глобальные переменные окружения
  env = {
    # Git всегда использует ssh из Nix
    GIT_SSH_COMMAND = "${pkgs.openssh}/bin/ssh";
    # Добавляем прокси для Tailscale
    ALL_PROXY = "socks5://localhost:1080/";
  };

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
