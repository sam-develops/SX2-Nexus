import discord
from discord.ext import commands, tasks
import aiohttp
import os

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = "UCMIR5FKPjkcRvTWtLYOR5Dw"
NOTIFY_CHANNEL_ID = 1466444174760087914


class YouTubeNotifier(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.live = False
        self.check_live.start()

    async def cog_unload(self):
        self.check_live.cancel()

    async def get_live_stream(self):
        url = (
            "https://www.googleapis.com/youtube/v3/search"
            f"?part=snippet&channelId={CHANNEL_ID}"
            "&eventType=live&type=video"
            f"&key={YOUTUBE_API_KEY}"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                data = await r.json()

        if not data.get("items"):
            return None

        return data["items"][0]

    @tasks.loop(minutes=2)
    async def check_live(self):
        channel = self.bot.get_channel(NOTIFY_CHANNEL_ID)
        if not channel:
            return

        stream = await self.get_live_stream()

        if stream and not self.live:
            self.live = True

            snippet = stream["snippet"]
            video_id = stream["id"]["videoId"]
            title = snippet["title"]
            channel_name = snippet["channelTitle"]
            thumbnail = snippet["thumbnails"]["high"]["url"]
            live_url = f"https://www.youtube.com/watch?v={video_id}"

            embed = discord.Embed(
                title="🔴 LIVE ON YOUTUBE",
                description=f"**[{title}]({live_url})**",
                color=discord.Color.red(),
                url=live_url,
                timestamp=discord.utils.utcnow(),
            )

            embed.set_author(
                name=channel_name,
                icon_url="https://www.youtube.com/s/desktop/fe2c1c27/img/favicon_144x144.png",
                url=f"https://www.youtube.com/channel/{CHANNEL_ID}",
            )

            embed.set_image(url=thumbnail)
            embed.add_field(
                name="📺 Watch Now",
                value=f"[Click here to join the live stream]({live_url})",
                inline=False,
            )

            await channel.send(embed=embed)

        if not stream:
            self.live = False

    @check_live.before_loop
    async def before_check_live(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(YouTubeNotifier(bot))
