# 02 — Docker

Installed using Docker's official convenience script, which sets up the
repository and installs the current stable release.

## Install

    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER

Log out and back in (or reboot) so the group membership takes effect. Verify:

    docker --version
    docker compose version

As installed:

- Docker version 29.9.2
- Docker Compose version v5.6.1

## Notes

- The convenience script is fine for a home server. For production, Docker's
  documentation recommends installing from the repository manually so upgrades
  are explicit.
- The `docker` group grants root-equivalent access. Every user in that group can
  mount arbitrary host paths into containers. Add users deliberately.
- No `/etc/docker/daemon.json` is used — defaults are sufficient for this setup.

## Containers

Two containers run:

- `jellyfin` — media streaming (see 04-jellyfin.md)
- `discordtorrentmanager` — Discord bot (see 06-discord-bot.md)

qBittorrent runs outside Docker as an AppImage (see 05-qbittorrent.md).

## Rebuilding and restarting

    docker ps
    docker logs --tail 50 <container>
    docker restart <container>
    docker stop <container> && docker start <container>

To rebuild the bot after changing its Dockerfile:

    cd ~/DiscordTorrentManager
    docker build -t discordtorrentmanager:latest .

Note: the running container bind-mounts `bot.py` from the host, so edits to
`bot.py` take effect on `docker restart` without a rebuild. A rebuild is only
needed when `Dockerfile`, `requirements.txt` or `app.py` change. This is
deliberate for development but non-obvious — documented in 07-gotchas.md.
