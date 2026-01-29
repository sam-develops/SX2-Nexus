import discord
from discord.ext import commands
from utils.config_manager import load_config, save_config

class AdminReset(commands.Cog):
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

    @commands.command(name="resetconfig", help="Reset all server configuration for this guild.")
    @commands.has_permissions(administrator=True)
    async def reset_config(self, ctx):
        gid = str(ctx.guild.id)

        if gid not in self.config or not self.config[gid]:
            await ctx.send("❌ No configuration found to reset.")
            return

        # Remove the guild's config
        self.config.pop(gid)
        save_config(self.config)
        await ctx.send("🔄 Server configuration has been reset successfully!")

async def setup(bot):
    await bot.add_cog(AdminReset(bot))
