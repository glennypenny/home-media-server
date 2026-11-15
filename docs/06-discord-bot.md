# 06 — Discord bot

The bot is a fork of JakeTurner616/DiscordTorrentManager, a GPLv3 project that
connects Discord to qBittorrent. It runs as the container
`discordtorrentmanager`.

## Why a fork

Jake's original project documents a `/magnet` command and a working `/search`
command. Neither worked as documented:

- `/magnet` was documented but not implemented in the code. The
  `handle_magnet_download` function existed, but no slash command called it.
- `/search` called `http://127.0.0.1:5000/torrents?q=...` — a Flask endpoint
  that returned bad or no data. Every search ended with "No Results Found".
- `handle_magnet_download` polled `http://127.0.0.1:5000/infoglobal` in a
  `while True:` loop to update a progress embed. That endpoint returned bad
  data, the loop threw, and every successful add displayed "Error 0" even
  though the torrent was downloading fine.

## The three fixes

### 1. /magnet — implement what was already documented

Added a new slash command that takes a magnet link and a category, validates
the link starts with `magnet:?`, and calls the existing (previously
unreachable) `handle_magnet_download`.

### 2. /search — swap the data source

Replaced:

    r = await run_blocking(requests.get, f"{API_URL}/torrents?q={query}", timeout=10)
    results = r.json()

with a helper `_search_1337x(query, category)` that uses the `py1337x` library
and returns the same dictionary shape the existing display code expects
(`title`, `size`, `seeders`, `leechers`, `date`, `magnet_link`). The display
code — embeds, emoji reactions, timeout handling — is unchanged.

The `/search` command depends on 1337x.to being reachable from the server.
In some regions the site is unreachable or rate-limited, in which case `/search`
returns no results. Magnet-link use via `/magnet` is unaffected. See
08-next-steps.md.

### 3. handle_magnet_download — remove the progress loop

The original version added the torrent, then entered a polling loop that
updated a Discord embed every 5 seconds. The loop's data source was broken.
Replaced with a single confirmation embed:

    async def handle_magnet_download(channel, magnet_link, category):
        try:
            await run_blocking(qbit.download, magnet_link, category)
            await channel.send(embed=discord.Embed(
                title="Torrent Added",
                description=f"Category: **{category}**\nCheck qBittorrent for progress.",
                color=discord.Color.green()
            ))
        except Exception as e:
            logger.exception("Download error")
            await channel.send(embed=discord.Embed(
                title="Error",
                description=f"`{type(e).__name__}: {e}`",
                color=discord.Color.red()
            ))

qBittorrent's own Web UI shows progress better than a Discord embed. The bot's
job is to accept links from Discord, not to be a monitoring dashboard.

## Summary

| Change | Lines affected | Problem solved |
| --- | --- | --- |
| Added /magnet command | ~20 added | Documented command did not exist |
| Replaced /search source with py1337x | 2 lines replaced, ~20-line helper added | Every search returned "No Results Found" |
| Simplified handle_magnet_download | ~60 replaced with ~12 | Cryptic "Error 0" after every add |

## Dependencies

`requirements.txt` adds `py1337x` (the PyPI package; imported as `import py1337x`).

The Dockerfile does unusual `discord` / `py-cord` package juggling — install
both, uninstall both, reinstall py-cord, uninstall `discord`. This is Jake's
original workaround for the package-name collision between `discord.py` and
`py-cord`. It works; do not "clean it up" without testing.

## Running

The container bind-mounts three host paths:

    docker run -d \
      --name discordtorrentmanager \
      --add-host=host.docker.internal:host-gateway \
      -v <bot-project-path>/config.ini:/app/config.ini \
      -v <bot-project-path>/bot.py:/app/bot.py \
      --restart unless-stopped \
      discordtorrentmanager:latest

- `config.ini` is mounted read-only-in-effect (nothing writes to it), containing
  the Discord token, guild ID, and qBittorrent credentials.
- `bot.py` is mounted directly so edits to the host file take effect on
  `docker restart` — no rebuild needed. Rebuild only when `Dockerfile`,
  `requirements.txt` or `app.py` change.
- `--add-host=host.docker.internal:host-gateway` lets the container reach
  services running on the host (qBittorrent) by hostname.

## Configuration

See `bot/config.ini.example` for the required keys. Copy to `config.ini` and
fill in real values — `config.ini` is git-ignored and must never be committed.

## Commands

- `/magnet <magnet-link> <category>` — add a torrent
- `/search <query> <category>` — search 1337x and show results with reactions
- Additional commands inherited from the upstream project (see `bot/README.md`)
