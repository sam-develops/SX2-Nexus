import discord
from discord.ext import commands
from utils.config_manager import load_config, save_config

class AdminLogs(commands.Cog):
    category = "Admin"
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    def get_guild(self, guild_id):
        """Get or create guild config"""
        gid = str(guild_id)
        if gid not in self.config:
            self.config[gid] = {}
        return self.config[gid]

    @commands.command(name="setlogchannel", help="Set the moderation log channel for the server.")
    @commands.has_permissions(administrator=True)
    async def set_log_channel(self, ctx, channel: discord.TextChannel):
        guild_cfg = self.get_guild(ctx.guild.id)
        guild_cfg["log_channel"] = channel.id
        save_config(self.config)
        await ctx.send(f"✅ Moderation log channel set to {channel.mention}")

    @commands.command(name="logchannel", help="Show the currently set moderation log channel.")
    async def show_log_channel(self, ctx):
        guild_cfg = self.get_guild(ctx.guild.id)
        channel_id = guild_cfg.get("log_channel")
        if not channel_id:
            await ctx.send("❌ No log channel has been set yet.")
            return
        channel = ctx.guild.get_channel(channel_id)
        if not channel:
            await ctx.send("❌ The previously set log channel no longer exists.")
            return
        await ctx.send(f"📌 Moderation log channel: {channel.mention}")


async def setup(bot):
    await bot.add_cog(AdminLogs(bot))
