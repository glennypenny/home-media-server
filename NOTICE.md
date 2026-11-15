# Attribution and derivation notice

## Discord bot

The code in `bot/` is derived from
[JakeTurner616/DiscordTorrentManager](https://github.com/JakeTurner616/DiscordTorrentManager),
licensed under the GNU General Public License v3.0. The original `LICENSE`
and `README.md` are preserved unmodified inside `bot/`.

Modifications by Glen Salmon:

1. Added the missing `/magnet` slash command.
2. Replaced the broken `/search` backend (a Flask endpoint that did not exist)
   with a working implementation using the `py1337x` library.
3. Simplified `handle_magnet_download` — removed the broken progress-polling
   loop that produced "Error 0" on every add.

Details in [docs/06-discord-bot.md](docs/06-discord-bot.md).

The repository as a whole is distributed under GPLv3 because it includes
GPLv3 code. Documentation and configuration examples authored by Glen Salmon
are under the same license for simplicity.

## Other credits

- Jellyfin — <https://jellyfin.org>
- qBittorrent — <https://www.qbittorrent.org>
- Samba — <https://www.samba.org>
- Pycord — <https://pycord.dev>
- py1337x — <https://github.com/hemantapkh/1337x>
