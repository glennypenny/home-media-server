# Installation guide

A complete, step-by-step walkthrough from a fresh Ubuntu install to a working
Discord bot responding in your server. Every command can be copy-pasted.

If you want the reasoning behind any step, each section links to the relevant
document in `docs/`.

## Before you start

You will need to replace three placeholders throughout this guide:

| Placeholder | What it is | How to find it |
| --- | --- | --- |
| `<your-username>` | Your Linux login name on the server | Run `whoami` on the server |
| `<server-ip>` | The server's LAN IP address | Run `hostname -I` on the server, use the first result |
| `<bot-project-path>` | Where the Discord bot lives on the server | You'll create this in step 7; a typical value is `/home/<your-username>/DiscordTorrentManager` |

Hardware: this guide was written against an HP Omen 15 laptop with Wi-Fi only.
Any x86_64 machine with a network connection should work; adapt the network
step if your hardware differs.

You will need:

- A USB stick (8 GB+) with the Ubuntu Desktop 24.04 LTS installer on it
- The target machine (the future server)
- Another device on the same network (to test access)
- A Discord account with a server where you have admin rights

## Step 1 — Install Ubuntu Desktop

Download Ubuntu Desktop 24.04 LTS from https://ubuntu.com/download/desktop and
write it to a USB stick (use Rufus on Windows, `dd` on Linux, or balenaEtcher
on macOS).

Boot the target machine from the USB stick and install Ubuntu Desktop with the
default options. Connect to your network (Wi-Fi or Ethernet) during install so
updates download.

Reboot into the fresh desktop. Open a terminal (`Ctrl+Alt+T`).

Why Desktop and not Server: see `docs/01-ubuntu.md`.

## Step 2 — Disable the GUI

The machine will now run headless despite being installed with a desktop.

    sudo systemctl set-default multi-user.target
    sudo reboot

After reboot you get a text login prompt instead of a graphical session. Log in.

If you need a graphical session later, run `sudo systemctl start gdm3` and switch
to it with `Ctrl+Alt+F2`.

## Step 3 — Update and install core packages

    sudo apt update
    sudo apt upgrade -y

Install Docker:

    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER

Log out and back in (or reboot) so the group change takes effect. Then verify:

    docker --version
    docker compose version

Install Samba:

    sudo apt install -y samba

Why these choices: see `docs/02-docker.md` and `docs/03-samba.md`.

## Step 4 — Create the folder structure

    sudo mkdir -p /srv/samba/share/sambashare
    sudo mkdir -p /srv/samba/share/sambashare/movies
    sudo mkdir -p /srv/samba/share/sambashare/tv
    sudo mkdir -p /srv/jellyfin/config
    sudo mkdir -p /srv/jellyfin/cache
    sudo chown -R $USER:$USER /srv/samba/share/sambashare /srv/jellyfin

Verify:

    ls -la /srv/samba/share/sambashare/
    ls -la /srv/jellyfin/

You should see `movies/` and `tv/` under the sambashare, and `config/` and
`cache/` under jellyfin, all owned by your user.

## Step 5 — Install qBittorrent and enable the Web UI

    cd ~/Downloads
    wget https://sourceforge.net/projects/qbittorrent/files/qbittorrent-win32/qbittorrent-5.3.0/qbittorrent-5.3.0_x86_64.AppImage/download -O qbittorrent.AppImage
    chmod +x qbittorrent.AppImage
    ./qbittorrent.AppImage

The qBittorrent window opens. In the app:

1. **Tools → Options → Web UI**
2. Tick **"Web User Interface (Remote control)"**
3. Set **Username**: `admin`
4. Set **Password**: choose something strong and note it down
5. Set **Port**: `8080`
6. Uncheck **"Only listen on localhost"**
7. Click **Apply** and **OK**

Close qBittorrent (`Ctrl+Q`). You'll start it again in step 8.

Verify it's listening:

    ss -tlnp | grep 8080

Expected: a line with `0.0.0.0:8080`. If it says `127.0.0.1:8080`, the "Only
listen on localhost" checkbox didn't save — reopen qBittorrent and re-check.

Why the AppImage: see `docs/05-qbittorrent.md`.

## Step 6 — Run Jellyfin

    docker run -d \
      --name jellyfin \
      -p 8096:8096 \
      -v /srv/jellyfin/config:/config \
      -v /srv/jellyfin/cache:/cache \
      -v /srv/samba/share/sambashare/movies:/media/movies:ro \
      -v /srv/samba/share/sambashare/tv:/media/tv:ro \
      --restart unless-stopped \
      jellyfin/jellyfin

Verify the container is running:

    docker ps --filter name=jellyfin

Now open `http://<server-ip>:8096` in a browser on another device (your laptop,
phone, or TV). Complete the first-run wizard:

1. Choose your language and display name
2. Add library → **Movies** → folder `/media/movies`
3. Add library → **TV Shows** → folder `/media/tv`
4. Finish the wizard

Why these mounts: see `docs/04-jellyfin.md`.

## Step 7 — Set up Samba

Create the share. The quickest way is via the GUI, but if you're headless now:

    sudo tee -a /etc/samba/smb.conf > /dev/null <<'EOF'

    [sambashare]
        comment = Samba on Ubuntu
        create mask = 0664
        directory mask = 0775
        path = /srv/samba/share/sambashare
        read only = No
        valid users = <your-username>
        write list = <your-username>
    EOF

Replace `<your-username>` with the value from "Before you start".

Set a Samba password (this is separate from your Linux login password):

    sudo smbpasswd -a <your-username>

Reload Samba and enable it at boot:

    sudo systemctl reload smbd
    sudo systemctl enable smbd

Verify from another machine on the network:

- Windows: open `\\<server-ip>\sambashare` in File Explorer
- macOS: Finder → Go → Connect to Server → `smb://<server-ip>/sambashare`
- Linux: `smb://<server-ip>/sambashare` in your file manager

You'll be prompted for the Samba password from `smbpasswd`.

Why usershares vs. smb.conf: see `docs/03-samba.md`.

## Step 8 — Clone and build the Discord bot

Choose a location on the server for the bot project and clone the fork:

    mkdir -p ~/DiscordTorrentManager
    cd ~/DiscordTorrentManager

Copy the bot files from this repo. If you cloned this repo to the server:

    cp -r ~/home-media-server/bot/* ~/DiscordTorrentManager/

(Adjust the first path if you cloned this repo elsewhere. `<bot-project-path>`
from "Before you start" should now equal `/home/<your-username>/DiscordTorrentManager`.)

Build the container image:

    cd <bot-project-path>
    docker build -t discordtorrentmanager:latest .

Verify:

    docker images | grep discordtorrentmanager

Why the build is needed: see `docs/06-discord-bot.md`.

## Step 9 — Configure the bot

Copy the placeholder config and edit it:

    cd <bot-project-path>
    cp config.ini.example config.ini
    nano config.ini

Fill in four values:

1. **`token`** — your Discord bot token. Get it from
   https://discord.com/developers/applications → your application → Bot → Reset
   Token. Copy the value (it's only shown once).
2. **`guild_id`** — the Discord server (guild) ID where slash commands will be
   registered. Right-click your server name in Discord → **Copy Server ID**
   (you must enable Developer Mode in Discord settings first).
3. **`user`** — qBittorrent Web UI username (from step 5, likely `admin`).
4. **`pass`** — qBittorrent Web UI password (from step 5).

Leave `host = http://<server-ip>:8080` as-is unless your server IP changes.

Save and exit.

**Never commit `config.ini`.** It contains live credentials. The repo's
`.gitignore` already excludes it.

Invite the bot to your Discord server:

1. Go to https://discord.com/developers/applications → your app → OAuth2 →
   URL Generator
2. Scopes: `bot` and `applications.commands`
3. Bot permissions: `Send Messages`, `Read Message History`
4. Copy the generated URL and open it in a browser to invite the bot

## Step 10 — Start qBittorrent and the bot

Start qBittorrent in the background so it keeps running after you close the
terminal:

    cd ~/Downloads
    nohup ./qbittorrent.AppImage > /dev/null 2>&1 &

Start the bot:

    docker run -d \
      --name discordtorrentmanager \
      --add-host=host.docker.internal:host-gateway \
      -v <bot-project-path>/config.ini:/app/config.ini \
      -v <bot-project-path>/bot.py:/app/bot.py \
      --restart unless-stopped \
      discordtorrentmanager:latest

Wait a few seconds, then check the logs:

    docker logs --tail 30 discordtorrentmanager

Look for these lines (order varies):

    Configuration loaded successfully.
    Connecting to qBittorrent host: http://<server-ip>:8080
    Backend running under Gunicorn
    Shard ID None has connected to Gateway
    glen_t_bot#XXXX online — connected to Discord Gateway.

If you see `Login failed: 204` before the "connected to Gateway" line, that's
a Pycord false positive and can be ignored.

If you see `Connection refused` repeatedly, qBittorrent is not reachable —
check step 5's `ss -tlnp | grep 8080` output again.

Why the volume mounts and the crash-loop behaviour: see `docs/07-gotchas.md`.

## Step 11 — Test in Discord

In your Discord server, in a channel the bot can see:

- Type `/status` — the bot should reply with an empty torrent list or a "no
  torrents" message.
- Type `/magnet <magnet-link> movies` — replace `<magnet-link>` with a legal
  magnet link (see note below). The bot should reply "Torrent Added" and the
  torrent should appear in qBittorrent.
- Type `/search <query> tv` — the bot should return search results. This
  depends on 1337x.to being reachable; if it returns no results, that's a known
  limitation, not a setup failure.

**Legal note:** only test with torrents you have the right to download — public
domain media, open-source software, or your own files. Downloading copyrighted
material without permission is illegal in the UK and most other jurisdictions.
The bot does not distinguish between legal and illegal torrents.

If the torrent appears in qBittorrent but not in Jellyfin, trigger a library
scan in Jellyfin: **Dashboard → Scan All Libraries**.

Why `/search` may fail: see `docs/08-next-steps.md`.

## Troubleshooting quick-reference

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| `docker: command not found` | Docker install failed, or you didn't log out/in after adding to the `docker` group | Re-run step 3; log out and back in |
| `ss -tlnp | grep 8080` shows nothing | qBittorrent isn't running | Start it: `cd ~/Downloads && ./qbittorrent.AppImage` |
| `ss -tlnp | grep 8080` shows `127.0.0.1:8080` | Web UI bound to localhost only | Reopen qBittorrent → Tools → Options → Web UI → uncheck "Only listen on localhost" |
| Bot logs show `Connection refused` every second, CPU ~100% | Bot can't reach qBittorrent — wrong IP in `config.ini`, or qBittorrent stopped | Check `hostname -I` matches `config.ini`'s `host` value; restart qBittorrent |
| Bot logs show `Login failed: 204` and then `connected to Gateway` | Harmless Pycord log ordering | Ignore |
| Bot logs show `Login failed: 204` and nothing else | Token is wrong or has been rotated | Regenerate the token in the Discord Developer Portal, update `config.ini`, restart the bot |
| Slash commands don't appear in Discord | Bot not invited, or guild ID wrong, or commands not synced yet | Check the OAuth2 invite in step 9; verify `guild_id` in `config.ini`; wait a minute and refresh Discord |
| `/search` always returns no results | 1337x.to unreachable from your region | Known limitation — use `/magnet` instead |
| Jellyfin shows no movies after download | Library scan hasn't run | Jellyfin → Dashboard → Scan All Libraries |
| Can't connect to Samba share from Windows | Firewall or wrong credentials | Check `sudo ufw status`; re-run `sudo smbpasswd -a <your-username>` |

For deeper troubleshooting, see `docs/07-gotchas.md`.
