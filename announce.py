import discord
from discord.ext import commands

class AdminAnnounce(commands.Cog):
    category = "Admin"
    """Send announcements via the bot. 
       Usage:- !announce <channel> <message>."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="announce", help="Send an announcement in a channel.")
    @commands.has_permissions(administrator=True)
    async def announce(self, ctx, channel: discord.TextChannel, *, message: str):
        embed = discord.Embed(
            title="📢 Announcement",
            description=message,
            color=0x5865F2
        )
        embed.set_footer(text=f"Announced by {ctx.author}", icon_url=ctx.author.avatar.url)
        await channel.send(embed=embed)
        await ctx.send(f"✅ Announcement sent in {channel.mention}", delete_after=5)

async def setup(bot):
    await bot.add_cog(AdminAnnounce(bot))
