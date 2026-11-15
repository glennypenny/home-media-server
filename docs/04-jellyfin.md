# 04 — Jellyfin

Jellyfin runs in Docker from the official `jellyfin/jellyfin` image. It mounts
config and cache directories for persistence, and the two media folders
read-only.

## Run command

    docker run -d \
      --name jellyfin \
      -p 8096:8096 \
      -v /srv/jellyfin/config:/config \
      -v /srv/jellyfin/cache:/cache \
      -v /srv/samba/share/sambashare/movies:/media/movies:ro \
      -v /srv/samba/share/sambashare/tv:/media/tv:ro \
      --restart unless-stopped \
      jellyfin/jellyfin

## Directory mapping

| Host path | Container path | Mode |
| --- | --- | --- |
| /srv/jellyfin/config | /config | rw |
| /srv/jellyfin/cache | /cache | rw |
| /srv/samba/share/sambashare/movies | /media/movies | ro |
| /srv/samba/share/sambashare/tv | /media/tv | ro |

The media mounts are read-only: Jellyfin never writes to them. New files appear
in Jellyfin's library after a scan (either scheduled or triggered manually from
Dashboard → Scan All Libraries).

## Web UI

`http://192.168.28.11:8096`

First-run wizard: create the admin user, then add libraries:

- Movies → folder `/media/movies`
- TV Shows → folder `/media/tv`

Do not add the parent directory `/srv/samba/share/sambashare` as a library — it
contains both library folders and would confuse Jellyfin's scanner.

## Transcoding

No hardware transcoding is configured. The Omen 15's GPU would require an
NVIDIA container runtime plus `--runtime nvidia` and additional environment
variables. Since the server is LAN-only and most client devices can decode
h264 directly, hardware transcoding is not currently needed. If 4K playback
or many concurrent streams become a problem, see
https://jellyfin.org/docs/general/post-install/transcoding/hardware-acceleration/nvidia/

## Upgrading

    docker pull jellyfin/jellyfin
    docker stop jellyfin && docker rm jellyfin
    # re-run the same docker run command above

Config and cache persist across upgrades because they are bind-mounted.

## Logs

    docker logs --tail 100 jellyfin
