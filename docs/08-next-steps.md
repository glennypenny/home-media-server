# 08 — Next steps

Planned improvements, not yet implemented.

## 1. Make /search reliable

The `/search` command depends on `py1337x`, which scrapes 1337x.to. From this
server's location, the site is often unreachable or rate-limited, so `/search`
frequently returns no results. `/magnet` is unaffected — pasting a magnet link
directly always works.

Possible fixes, none of which have been attempted yet:

- Switch to an alternative search source (e.g. a different indexer library) or
  a small HTTP proxy in a location where 1337x is reachable.
- Run a proxy/VPN for the container only, so outgoing HTTP from the bot uses a
  route that can reach 1337x.
- Drop `/search` entirely and document `/magnet` as the primary workflow. This
  is the simplest option — the bot does not need a search engine to work.

## 2. Move qBittorrent out of ~/Downloads

The AppImage lives in a user download folder and is started by hand. If the
file is moved, deleted, or the terminal is closed, qBittorrent stops and the
bot loses its dependency.

Planned fixes:

- Move the AppImage to `/opt/qbittorrent/` (root-owned, service location).
- Wrap it in a systemd service (either user or system) so it starts on boot,
  restarts on failure, and does not depend on a terminal being open.

## 3. Add a Batocera game console

A small, curated game console for the family, controlled the same way media is:
a whitelist of what can be played, served over the LAN. Batocera is the
intended platform.

High-level plan, not yet started:

- Dedicate a device (an older PC or a single-board computer) to Batocera.
- Expose its ROM library over the LAN via a second Samba share.
- Restrict the ROM library to pre-approved games (the same principle as the
  media library — a whitelist, not a free-for-all).
- Add a "games" category to the Discord bot for ROM downloads via magnet links
  if this turns out to be useful.

## 4. Optional: pin dependency versions

`requirements.txt` currently uses unpinned versions. Pin them from the running
container (`pip freeze`) so rebuilds are reproducible. Deferred because it is
not blocking anything.
