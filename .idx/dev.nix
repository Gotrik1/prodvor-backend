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
          # В IDX здесь просто команда; venv активируй в стартовом скрипте
          command = [ "bash" "-c" "python main.py" ];
          manager = "web";
        };
      };
    };
  };
}
