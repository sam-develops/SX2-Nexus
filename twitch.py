import discord
from discord.ext import commands, tasks
import aiohttp
import os

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")
TWITCH_USERNAME = "sx2official"
NOTIFY_CHANNEL_ID = 1466444073626898654


class TwitchNotifier(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.access_token = None
        self.live = False
        self.check_stream.start()

    async def cog_unload(self):
        self.check_stream.cancel()

    async def get_access_token(self):
        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": TWITCH_CLIENT_ID,
            "client_secret": TWITCH_CLIENT_SECRET,
            "grant_type": "client_credentials",
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, params=params) as r:
                data = await r.json()
                self.access_token = data.get("access_token")

    async def fetch_stream(self):
        if not self.access_token:
            await self.get_access_token()

        headers = {
            "Client-ID": TWITCH_CLIENT_ID,
            "Authorization": f"Bearer {self.access_token}",
        }

        url = f"https://api.twitch.tv/helix/streams?user_login={TWITCH_USERNAME}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as r:
                if r.status == 401:
                    self.access_token = None
                    return None

                data = await r.json()

        if not data.get("data"):
            return None

        return data["data"][0]

    @tasks.loop(minutes=2)
    async def check_stream(self):
        channel = self.bot.get_channel(NOTIFY_CHANNEL_ID)
        if not channel:
            return

        stream = await self.fetch_stream()

        if stream and not self.live:
            self.live = True

            title = stream["title"]
            game = stream["game_name"]
            url = f"https://twitch.tv/{TWITCH_USERNAME}"

            embed = discord.Embed(
                title="🔴 LIVE ON TWITCH",
                description=f"**{TWITCH_USERNAME}** is now live!",
                color=discord.Color.purple(),
                url=url,
                timestamp=discord.utils.utcnow(),
            )

            embed.add_field(name="🎮 Game", value=game, inline=True)
            embed.add_field(name="📢 Title", value=title, inline=False)

            embed.set_thumbnail(
                url="https://static.twitchcdn.net/assets/favicon-32-e29e246c157142c94346.png"
            )

            await channel.send(embed=embed)  # type: ignore

        if not stream:
            self.live = False

    @check_stream.before_loop
    async def before_check_stream(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(TwitchNotifier(bot))
