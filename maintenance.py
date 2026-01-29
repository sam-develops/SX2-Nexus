# cogs/owner/maintenance.py
import discord
from discord.ext import commands
import asyncio
import traceback

class Maintenance(commands.Cog):
    category = "Owner"
    """Owner-only Maintenance and Debug commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # -------------------------
    # Shutdown
    # -------------------------
    @commands.command(name="shutdown", help="Shuts down the bot (Owner only).")
    @commands.is_owner()
    async def shutdown(self, ctx):
        await ctx.send("⚠️ Shutting down the bot...")
        await self.bot.close()

    # -------------------------
    # Restart (requires hosting support)
    # -------------------------
    @commands.command(name="restart", help="Restarts the bot (Owner only).")
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.send("⚠️ Restarting the bot...")
        # Only works if your host restarts the process automatically
        await self.bot.close()

    # -------------------------
    # Cog management
    # -------------------------
    @commands.command(name="load", help="Load a cog (Owner only).")
    @commands.is_owner()
    async def load_cog(self, ctx, cog: str):
        try:
            await self.bot.load_extension(cog)
            await ctx.send(f"✅ Loaded cog `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to load `{cog}`:\n```py\n{e}\n```")

    @commands.command(name="unload", help="Unload a cog (Owner only).")
    @commands.is_owner()
    async def unload_cog(self, ctx, cog: str):
        try:
            await self.bot.unload_extension(cog)
            await ctx.send(f"✅ Unloaded cog `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to unload `{cog}`:\n```py\n{e}\n```")

    @commands.command(name="reload", help="Reload a cog (Owner only).")
    @commands.is_owner()
    async def reload_cog(self, ctx, cog: str):
        try:
            await self.bot.reload_extension(cog)
            await ctx.send(f"✅ Reloaded cog `{cog}`")
        except Exception as e:
            await ctx.send(f"❌ Failed to reload `{cog}`:\n```py\n{e}\n```")

    # -------------------------
    # Bot Status / Debug
    # -------------------------
    @commands.command(name="status", help="Shows bot status and info (Owner only).")
    @commands.is_owner()
    async def status(self, ctx: commands.Context):
        """Shows total servers, members, and latency."""
        guild_count = len(self.bot.guilds)
        # Sum member counts safely, ignoring None
        member_count = sum(guild.member_count or 0 for guild in self.bot.guilds)
        latency_ms = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="🤖 Bot Status",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Servers", value=guild_count)
        embed.add_field(name="Total Members", value=member_count)
        embed.add_field(name="Latency", value=f"{latency_ms} ms")
        embed.add_field(name="Discord.py Version", value=discord.__version__)
        await ctx.send(embed=embed)

    # -------------------------
    # Eval (optional, advanced debugging)
    # -------------------------
    @commands.command(name="eval", help="Evaluate Python code (Owner only).")
    @commands.is_owner()
    async def _eval(self, ctx, *, code: str):
        """Dangerous! Only for trusted bot owner."""
        env = {
            "bot": self.bot,
            "ctx": ctx,
            "discord": discord,
            "__import__": __import__,
        }
        try:
            result = eval(code, env)
            if asyncio.iscoroutine(result):
                result = await result
            await ctx.send(f"✅ Result:\n```py\n{result}\n```")
        except Exception as e:
            await ctx.send(f"❌ Error:\n```py\n{traceback.format_exc()}\n```")

async def setup(bot: commands.Bot):
    await bot.add_cog(Maintenance(bot))
