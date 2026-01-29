# cogs/utilities/utilities.py
import discord
from discord.ext import commands
from datetime import datetime
from typing import Optional


class Utilities(commands.Cog):
    """Utility commands for all users."""

    category = "Utilities"

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -------------------------
    # -------------------------

    # -------------------------
    # Server Info
    # -------------------------
    @commands.command(name="serverinfo", help="Get information about the server.")
    async def serverinfo(self, ctx: commands.Context):
        guild = ctx.guild
        if guild is None:
            await ctx.send("❌ Could not fetch server info.")
            return

        roles = (
            [r.name for r in guild.roles if r.name != "@everyone"]
            if guild.roles
            else []
        )
        owner = guild.owner.mention if guild.owner else "Unknown"
        icon_url = guild.icon.url if guild.icon else None
        member_count = guild.member_count or "Unknown"
        created_at = (
            guild.created_at.strftime("%Y-%m-%d") if guild.created_at else "Unknown"
        )

        embed = discord.Embed(
            title=f"🌐 Server Info: {guild.name}",
            color=discord.Color.purple(),
            timestamp=datetime.utcnow(),
        )
        embed.set_thumbnail(url=icon_url)
        embed.add_field(name="ID", value=guild.id, inline=True)
        embed.add_field(name="Owner", value=owner, inline=True)
        embed.add_field(name="Members", value=member_count, inline=True)
        embed.add_field(name="Roles", value=len(roles), inline=True)
        embed.add_field(name="Created At", value=created_at, inline=True)
        await ctx.send(embed=embed)

    # -------------------------
    # Avatar
    # -------------------------
    @commands.command(name="avatar", help="Get the avatar of a user.")
    async def avatar(
        self, ctx: commands.Context, member: Optional[discord.Member] = None
    ):
        member = member or ctx.author  # type: ignore
        if member is None:
            await ctx.send("❌ Could not fetch avatar.")
            return

        embed = discord.Embed(
            title=f"{member}'s Avatar",
            color=discord.Color.teal(),
            timestamp=datetime.utcnow(),
        )
        embed.set_image(url=member.display_avatar.url if member.display_avatar else "")
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Utilities(bot))
