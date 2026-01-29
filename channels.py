import discord
from discord.ext import commands


class AdminChannels(commands.Cog):
    category = "Admin"
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="lock")
    @commands.has_permissions(administrator=True)
    async def lock_channel(self, ctx):
        """Lock the current channel / usage :- !lock or !lock #channelname."""
        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=False
        )
        await ctx.send("🔒 Channel locked.")

    @commands.command(name="unlock")
    @commands.has_permissions(administrator=True)
    async def unlock_channel(self, ctx):
        """Unlock the current channel / usage :- !unlock or !lock #channelname."""
        await ctx.channel.set_permissions(
            ctx.guild.default_role,
            send_messages=True
        )
        await ctx.send("🔓 Channel unlocked.")

    @commands.command(name="slowmode")
    @commands.has_permissions(administrator=True)
    async def slowmode(self, ctx, seconds: int):
        """slow down channel text messaging. usage:- !slowmode 30sec"""
        await ctx.channel.edit(slowmode_delay=seconds)
        await ctx.send(f"🐢 Slowmode set to `{seconds}` seconds.")


async def setup(bot):
    await bot.add_cog(AdminChannels(bot))
