import discord
from discord.ext import commands
from utils.config_manager import load_config, save_config


class AdminConfig(commands.Cog):
    category = "Admin"
    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    def get_guild(self, guild_id):
        gid = str(guild_id)
        if gid not in self.config:
            self.config[gid] = {}
        return self.config[gid]

    @commands.command(name="setprefix")
    @commands.has_permissions(administrator=True)
    async def set_prefix(self, ctx, prefix: str):
        """Change bot prefix per server"""
        guild = self.get_guild(ctx.guild.id)
        guild["prefix"] = prefix
        save_config(self.config)
        await ctx.send(f"✅ Prefix set to `{prefix}`")

    @commands.command(name="config")
    async def show_config(self, ctx):
        """Shows current server configuration in an embed:
        Prefix
        Admin role
        Mod role
        Log channel
        Enabled features"""
        guild = self.get_guild(ctx.guild.id)
        embed = discord.Embed(
            title="⚙️ Server Configuration",
            color=discord.Color.green()
        )

        embed.add_field(
            name="Prefix",
            value=guild.get("prefix", "!"),
            inline=False
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(AdminConfig(bot))
