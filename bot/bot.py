#!/usr/bin/env python3
"""
Discord Torrent Manager Bot (Ultra-Stable Edition)
--------------------------------------------------
Reliable torrent manager with qBittorrent integration.
All blocking I/O offloaded to background threads for heartbeat safety.
Auto-reconnect, latency monitoring, and fault-tolerant loops.
"""

import sys, functools, asyncio, configparser, logging, humanize, requests, discord
from discord import Option, ApplicationContext
from discord.ext import commands
from urllib.parse import parse_qsl, urlencode
import py1337x

# ──────────────────────────────────────────────────────────────
# LOGGING SETUP
# ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("torrentbot")

# ──────────────────────────────────────────────────────────────
# CONFIGURATION
# ──────────────────────────────────────────────────────────────
config = configparser.ConfigParser()
config.read("config.ini")
try:
    bot_token = config.get("Bot", "token")
    guild_ids = [int(g.strip()) for g in config.get("Bot", "guild_id").split(",")]
    qb_host = config.get("qbit", "host").rstrip("/")
    qb_user = config.get("qbit", "user")
    qb_pass = config.get("qbit", "pass")
except Exception as e:
    logger.critical("Configuration error: %s", e)
    sys.exit(1)

API_URL = "http://127.0.0.1:5000"
emoji_list = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

# ──────────────────────────────────────────────────────────────
# UTILITIES
# ──────────────────────────────────────────────────────────────
async def run_blocking(func, *args, **kwargs):
    """Run blocking functions in executor to avoid heartbeat stalls."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, functools.partial(func, *args, **kwargs))

def trim_magnet(magnet_link: str, max_trackers: int = 7, max_len: int = 1024) -> str:
    if not magnet_link.startswith("magnet:?"):
        return magnet_link
    try:
        base, query = magnet_link.split("?", 1)
        params = parse_qsl(query)
        infohash = [p for p in params if p[0] in ("xt", "dn")]
        trackers = [p for p in params if p[0] == "tr"][:max_trackers]
        others = [p for p in params if p[0] not in ("xt", "dn", "tr")]
        new_params = infohash + trackers + others
        out = f"{base}?{urlencode(new_params, doseq=True)}"
        return out if len(out) <= max_len else out[:max_len-3] + "..."
    except Exception as e:
        logger.warning("Trim failed: %s", e)
        return magnet_link[:max_len-3] + "..."

# ──────────────────────────────────────────────────────────────
# QBITTORRENT SESSION
# ──────────────────────────────────────────────────────────────
class QbitSession:
    def __init__(self, host, user, password):
        self.host, self.user, self.password = host, user, password
        self.session = requests.Session()
        self.session.headers.update({
            "Referer": host, "Origin": host,
            "User-Agent": "Mozilla/5.0 (DiscordBot)"
        })

    def login(self):
        try:
            r = self.session.post(f"{self.host}/api/v2/auth/login",
                data={"username": self.user, "password": self.password}, timeout=10)
            if r.status_code == 200:
                logger.info("✅ Authenticated with qBittorrent")
            else:
                logger.error("Login failed: %s %s", r.status_code, r.text)
        except Exception as e:
            logger.error("Login exception: %s", e)

    def ensure(self):
        try:
            r = self.session.get(f"{self.host}/api/v2/app/version", timeout=5)
            if r.status_code != 200:
                self.login()
        except Exception:
            self.login()

    def download(self, magnet, category):
        self.ensure()
        try:
            r = self.session.post(f"{self.host}/api/v2/torrents/add",
                data={"urls": magnet, "category": category.lower()}, timeout=10)
            if r.status_code == 200:
                logger.info("Torrent added to %s", category)
            else:
                logger.error("Add failed: %s %s", r.status_code, r.text)
        except Exception as e:
            logger.error("Send error: %s", e)

qbit = QbitSession(qb_host, qb_user, qb_pass)
qbit.login()

# ──────────────────────────────────────────────────────────────
# DISCORD BOT SETUP
# ──────────────────────────────────────────────────────────────
intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")

# ──────────────────────────────────────────────────────────────
# HEARTBEAT + RECONNECT MONITORING
# ──────────────────────────────────────────────────────────────
@bot.event
async def on_ready():
    logger.info("🤖 %s online — connected to Discord Gateway.", bot.user)
    bot.loop.create_task(monitor_latency())

@bot.event
async def on_disconnect():
    logger.warning("⚠️ Lost connection to Discord gateway (shard closed). Reconnecting...")

@bot.event
async def on_resumed():
    logger.info("🔄 Connection resumed successfully.")

@bot.event
async def on_error(event, *args, **kwargs):
    logger.exception("Unhandled error in event %s", event)

async def monitor_latency():
    """Periodic heartbeat monitor."""
    await bot.wait_until_ready()
    while not bot.is_closed():
        logger.info(f"💓 Heartbeat latency: {bot.latency * 1000:.0f} ms")
        await asyncio.sleep(60)

# ──────────────────────────────────────────────────────────────
# TORRENT PROGRESS HANDLER
# ──────────────────────────────────────────────────────────────
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

# ──────────────────────────────────────────────────────────────
# MAGNET COMMAND
# ──────────────────────────────────────────────────────────────
@bot.slash_command(name="magnet", description="Add a torrent via magnet link.", guild_ids=guild_ids)
async def magnet(
    ctx: ApplicationContext,
    link: Option(str, "The magnet link", required=True),
    category: Option(str, "qBittorrent category", required=True)
):
    if not link.startswith("magnet:?"):
        await ctx.respond(embed=discord.Embed(
            title="Invalid Link",
            description="That doesn't look like a magnet link.",
            color=discord.Color.red()
        ), ephemeral=True)
        return

    await ctx.respond(embed=discord.Embed(
        title="Adding Torrent",
        description=f"Category: **{category}**",
        color=discord.Color.blurple()
    ))
    bot.loop.create_task(handle_magnet_download(ctx.channel, link, category))

# ──────────────────────────────────────────────────────────────
# SEARCH COMMAND
# ──────────────────────────────────────────────────────────────
@bot.slash_command(name="search", description="Search for torrents.", guild_ids=guild_ids)
async def search(
    ctx: ApplicationContext,
    query: Option(str, "Specify search query", required=True),
    category: Option(str, "Category to search", required=True, choices=["TV", "Movies", "Music", "Games", "Apps"])
):
    logger.info("Search query: %s (category: %s)", query, category)
    await ctx.respond(embed=discord.Embed(title="Searching...", color=discord.Color.blue()), ephemeral=True)

    try:
        results = await run_blocking(_search_1337x, query, category)
        if not results:
            await ctx.send(embed=discord.Embed(
                title="No Results Found", description="Try another search.",
                color=discord.Color.orange()
            ))
            return

        await ctx.send(embed=discord.Embed(
            title="⚠️ Provider Notice",
            description="Results from **1377x.to**; react below to add torrent (auto-timeout 60s).",
            color=discord.Color.gold()
        ))

        sent_messages = []
        for i, res in enumerate(results[:len(emoji_list)]):
            e = discord.Embed(title=res["title"], color=discord.Color.blurple())
            e.add_field(name="Size", value=res["size"], inline=True)
            e.add_field(name="Seeders", value=res["seeders"], inline=True)
            e.add_field(name="Leechers", value=res["leechers"], inline=True)
            e.add_field(name="Date", value=res["date"], inline=True)
            safe_magnet = trim_magnet(res["magnet_link"])
            e.add_field(name="Magnet Link", value=f"```{safe_magnet}```", inline=False)
            m = await ctx.send(embed=e)
            await m.add_reaction(emoji_list[i])
            sent_messages.append(m)

        def check(reaction, user):
            return user == ctx.user and str(reaction.emoji) in emoji_list and reaction.message in sent_messages

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send(embed=discord.Embed(
                title="⌛ Timeout", description="No selection was made within 60 seconds.",
                color=discord.Color.dark_grey()
            ))
            return

        msg = reaction.message
        magnet_field = next((f for f in msg.embeds[0].fields if f.name == "Magnet Link"), None)
        if magnet_field:
            magnet = magnet_field.value.strip("```")
            await ctx.send(embed=discord.Embed(
                title="Torrent Added via Reaction",
                description="Added to **Movie** category. Fetching progress...",
                color=discord.Color.green()
            ))
            bot.loop.create_task(handle_magnet_download(ctx.channel, magnet, "Movie"))
        else:
            await ctx.send(embed=discord.Embed(
                title="Error", description="Could not extract magnet link.", color=discord.Color.red()
            ))

    except Exception as e:
        logger.error("Search error: %s", e)
        await ctx.send(embed=discord.Embed(title="Error", description=str(e), color=discord.Color.red()))

def _search_1337x(query, category):
    client = py1337x.Py1337x()
    cat = {
        "TV":     py1337x.category.TV,
        "Movies": py1337x.category.MOVIES,
        # ...
    }.get(category, py1337x.category.TV)

    logger.info("Searching 1337x for '%s' in category '%s'", query, category)
    found = client.search(query, sort_by=py1337x.sort.SEEDERS, category=cat)
    
    # Log how many items the library found
    logger.info("1337x returned %d raw items", len(found.items))
    
    out = []
    for item in found.items[:5]:
        logger.info("Processing item: %s", item.name)
        try:
            info = client.info(torrent_id=item.torrent_id)
            magnet = info.magnet_link
            logger.info("Got magnet for %s", item.name)
        except Exception as e:
            logger.warning("Failed to get info for %s: %s", item.name, e)
            magnet = None
        if magnet:
            out.append({...})
    logger.info("Returning %d results after filtering", len(out))
    return out

# ──────────────────────────────────────────────────────────────
# MAIN ENTRY
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    while True:
        try:
            bot.run(bot_token, reconnect=True)
        except Exception as e:
            logger.critical("Bot crashed: %s. Restarting in 10s...", e)
            asyncio.run(asyncio.sleep(10))
