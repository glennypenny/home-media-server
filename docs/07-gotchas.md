# 07 — Known gotchas

Operational quirks of this setup. Not bugs — behaviours that are non-obvious
and worth knowing.

## The bot's qBittorrent host is hardcoded

The bot reads `host` from `config.ini`:

    host = http://192.168.28.11:8080

If the server's LAN IP changes (different Wi-Fi network, router DHCP
reassignment), the bot tries to connect to the old address and fails.
Symptoms in `docker logs discordtorrentmanager`:

    Connecting to qBittorrent host: http://192.168.28.11:8080
    Failed to init qBittorrent client: ... Connection refused
    Worker (pid:...) exited with code 1.

The gunicorn worker respawns in a loop, so `docker stats` shows the container
pinned near 100% CPU even though nothing useful is happening.

Fix: confirm the server's current IP (`hostname -I`), update `config.ini`
if it has changed, then `docker restart discordtorrentmanager`.

Prevent: either reserve a DHCP lease for the Omen's MAC on the router, or
use a hostname instead of an IP (e.g. `http://server.local:8080` via mDNS).

## qBittorrent is a foreground process

The AppImage runs in whichever terminal launched it. Closing the terminal
(or logging out) stops qBittorrent, and the bot fails to connect until it is
restarted. This is documented as an operational note, not a fix — see
08-next-steps.md for the planned improvement.

## Categories write directly into the library

qBittorrent categories are set to save straight into the Jellyfin library
folders. This means a partially-downloaded file is briefly visible to Jellyfin
during download. Jellyfin will typically fail to scan it until it's complete,
then pick it up on the next scan, so this is mostly cosmetic — but it's why a
file can appear in Jellyfin's library with a "0 min" runtime for a few minutes.

## The Docker volume mount overrides the image

The `discordtorrentmanager` container mounts `bot.py` from the host over the
copy baked into the image. Code changes to `bot.py` therefore take effect
immediately on `docker restart` — no rebuild required. But this means the
running code is not what is inside the image. Anyone debugging by inspecting
the image will see stale code. Rebuild when the difference matters.

## "Login failed: 204" from Pycord

The bot's startup log contains:

    ERROR - Login failed: 204

This is logged before the successful gateway connection, and it is a false
positive in this setup — the actual connection succeeds immediately afterwards
(`Shard ID None has connected to Gateway`, `glen_t_bot#6539 online`). It
appears to be an internal REST probe in Pycord. Not a problem; not fixed.

## "PyNaCl, davey are not installed, voice will NOT be supported"

A warning from Pycord at startup. Voice support is not needed for this bot.
Ignore.

## No hardware transcoding in Jellyfin

Jellyfin's image has no NVIDIA runtime configured. Software transcoding is
used. Fine for LAN playback at typical resolutions; see 04-jellyfin.md if that
becomes a limit.
