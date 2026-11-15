# Docker run commands

The exact commands used to bring up each service. These are the commands that
produced the running containers, with personal paths replaced by placeholders.

Placeholders used below:

- `<your-username>` — the Linux login user on the server
- `<bot-project-path>` — where you cloned/forked the Discord bot
  (e.g. `/home/<your-username>/DiscordTorrentManager`)
- `<sambashare-path>` — the root of the shared media directory
  (e.g. `/srv/samba/share/sambashare`)
- `<jellyfin-config-path>` — where Jellyfin stores its database and metadata
  (e.g. `/srv/jellyfin/config`)
- `<jellyfin-cache-path>` — where Jellyfin stores transcoded cache
  (e.g. `/srv/jellyfin/cache`)

## qBittorrent

Not a container. An AppImage launched from the host:

    cd Downloads/
    ./qbittorrent-5.3.0_x86_64.AppImage

The process runs in the foreground of whichever terminal launched it. Closing
the terminal stops qBittorrent and the Discord bot will lose its dependency.

## Jellyfin

    docker run -d \
      --name jellyfin \
      -p 8096:8096 \
      -v <jellyfin-config-path>:/config \
      -v <jellyfin-cache-path>:/cache \
      -v <sambashare-path>/movies:/media/movies:ro \
      -v <sambashare-path>/tv:/media/tv:ro \
      --restart unless-stopped \
      jellyfin/jellyfin

Web UI: `http://<server-ip>:8096` (e.g. `http://192.168.1.100:8096`).

## Discord Torrent Manager

    docker run -d \
      --name discordtorrentmanager \
      --add-host=host.docker.internal:host-gateway \
      -v <bot-project-path>/config.ini:/app/config.ini \
      -v <bot-project-path>/bot.py:/app/bot.py \
      --restart unless-stopped \
      discordtorrentmanager:latest

The container image is built separately (see `docs/06-discord-bot.md`):

    cd <bot-project-path>
    docker build -t discordtorrentmanager:latest .
