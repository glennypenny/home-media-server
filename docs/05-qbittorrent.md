# 05 — qBittorrent

qBittorrent runs as an AppImage on the host, not in Docker. This was chosen
for simplicity — the AppImage is self-contained and requires no installation.

## Running

    cd ~/Downloads
    ./qbittorrent-5.3.0_x86_64.AppImage

The process runs in the foreground. Closing the terminal stops the torrent
client and, unless it restarts, the Discord bot will fail to connect to it.

## Web UI

Enabled in Tools → Options → Web UI:

- Bind address: all interfaces (0.0.0.0)
- Port: 8080
- Username: admin
- Password: set (used by the Discord bot)

Accessible at `http://192.168.28.11:8080` from any LAN device.

If the Web UI is bound to 127.0.0.1 instead, the Discord bot (running inside
a Docker container) cannot reach it. This is the most common cause of the bot
failing to connect.

## Save paths and categories

Two categories are configured:

| Category | Save path (host) |
| --- | --- |
| movies | /srv/samba/share/sambashare/movies |
| tv | /srv/samba/share/sambashare/tv |

The Discord bot passes the category name when adding a torrent, so qBittorrent
saves directly into the Jellyfin library folder. There is no staging step:
downloads appear in the library as soon as the first byte is written.

This is documented as a known trade-off in 07-gotchas.md.

## Known operational note

The AppImage lives in `~/Downloads/`, which is a normal user download folder —
not a service location. If the file is moved or removed, the Web UI disappears
and the bot breaks. A move to `/opt/qbittorrent/` with a systemd unit is listed
in 08-next-steps.md.

## Config location

qBittorrent's own settings are stored under
`~/.config/qBittorrent/qBittorrent.conf`, not inside this repository.
