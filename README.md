# Home Media Server

A self-hosted, LAN-only media server for a family: torrents downloaded via a
Discord bot land in a shared folder, Samba exposes that folder to devices on
the network, and Jellyfin streams it to TVs, phones and tablets. The system
runs on a repurposed HP Omen 15 laptop running Ubuntu Desktop 24.04 LTS with
the GUI disabled.

The whole stack is deliberately **not exposed to the internet**. The only
out-of-LAN entry point is a Discord bot restricted to a hard-coded list of
user IDs.

## Architecture
LAN only (your_ip)
│
You (mobile) ──Discord──▶ Discord bot (Docker) ──▶ qBittorrent (AppImage)
│
▼
/srv/samba/share/sambashare
├── movies
└── tv
│
┌─────────────────────────────┤
▼ ▼
Samba share Jellyfin (Docker)
│ │
▼ ▼
Windows / macOS / Linux TV / phone / tablet

- **qBittorrent** runs as an AppImage on the host, Web UI on port 8080.
  Categories `movies` and `tv` save directly into the shared folders.
- **Jellyfin** runs in Docker, mounts the media folders read-only, streams to
  any device on the LAN.
- **Samba** exposes `/srv/samba/share/sambashare` as a network share.
- **Discord bot** is a fork of
  [JakeTurner616/DiscordTorrentManager](https://github.com/JakeTurner616/DiscordTorrentManager)
  with three fixes. It accepts `/magnet` and `/search` commands from
  whitelisted users and drives qBittorrent via its Web API.

## What's in this repo

| Path | Purpose |
| --- | --- |
| `docs/01-ubuntu.md` | OS choice: why Ubuntu Desktop, not Server |
| `docs/02-docker.md` | Docker installation |
| `docs/03-samba.md` | Samba share setup |
| `docs/04-jellyfin.md` | Jellyfin container |
| `docs/05-qbittorrent.md` | qBittorrent AppImage and Web UI |
| `docs/06-discord-bot.md` | The bot and its three fixes |
| `docs/07-gotchas.md` | Known operational quirks |
| `docs/08-next-steps.md` | Planned improvements |
| `bot/` | The Discord bot (forked, GPLv3) |
| `samba/smb.conf.example` | Sanitised Samba config |
| `docker-run-commands.md` | The exact `docker run` commands used |

## Security model

This stack assumes a trusted home LAN and an untrusted internet. No ports are
forwarded. The Discord bot does not listen on any port — it reaches out to
Discord, not the other way around. Only Discord user IDs listed in
`bot/config.ini` can issue commands. qBittorrent's Web UI is password-protected.

Torrent downloads are inherently abusable: any whitelisted user can add any
magnet link. The whitelist is therefore the primary security boundary.

## Attribution

The Discord bot in `bot/` is derived from
[JakeTurner616/DiscordTorrentManager](https://github.com/JakeTurner616/DiscordTorrentManager)
(GPLv3). See [NOTICE.md](NOTICE.md) and [bot/README.md](bot/README.md) for
the original project's documentation.

## License

GPLv3 — see [LICENSE](LICENSE).
