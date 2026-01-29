import discord
from discord.ext import commands
import psutil
import platform
import datetime

class BotInfo(commands.Cog):
    category = "Admin"
    """Shows bot statistics and information. Usage: !botinfo"""

    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.datetime.utcnow()

    def get_uptime(self):
        delta = datetime.datetime.utcnow() - self.start_time
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours}h {minutes}m {seconds}s"

    @commands.command(name="botinfo", help="Display bot statistics and uptime.")
    @commands.has_permissions(administrator=True)
    async def info(self, ctx):
        embed = discord.Embed(
            title="🤖 Bot Information",
            color=0x5865F2,
            timestamp=datetime.datetime.utcnow()
        )

        # General info
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Bot ID", value=self.bot.user.id, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(set(self.bot.get_all_members())), inline=True)
        embed.add_field(name="Uptime", value=self.get_uptime(), inline=True)
        embed.add_field(name="Latency", value=f"{round(self.bot.latency*1000)}ms", inline=True)

        # System info
        embed.add_field(name="Python Version", value=platform.python_version(), inline=True)
        embed.add_field(name="Platform", value=f"{platform.system()} {platform.release()}", inline=True)
        embed.add_field(name="CPU Usage", value=f"{psutil.cpu_percent()}%", inline=True)
        embed.add_field(name="Memory Usage", value=f"{round(psutil.virtual_memory().percent)}%", inline=True)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(BotInfo(bot))
