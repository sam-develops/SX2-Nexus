import discord
from discord.ext import commands
from pathlib import Path
import json

# -------------------------
# Config file
# -------------------------
DATA_DIR = Path("data")
SETTINGS_FILE = DATA_DIR / "server_roles.json"

DATA_DIR.mkdir(exist_ok=True)
if not SETTINGS_FILE.exists():
    SETTINGS_FILE.write_text("{}")

def load_config():
    try:
        return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}

def save_config(data):
    SETTINGS_FILE.write_text(json.dumps(data, indent=4))


class ServerSettings(commands.Cog):
    """Admin commands to configure server settings."""
    category = "Admin"

    def __init__(self, bot):
        self.bot = bot
        self.config = load_config()

    def get_guild_cfg(self, guild_id):
        return self.config.setdefault(str(guild_id), {})

    # -------------------------
    # Set welcome channel
    # -------------------------
    @commands.command(name="setwelcomechannel", help="Set the channel for welcome messages.")
    @commands.has_permissions(administrator=True)
    async def set_welcome_channel(self, ctx, channel: discord.TextChannel):
        cfg = self.get_guild_cfg(ctx.guild.id)
        cfg["welcome_channel"] = channel.id
        save_config(self.config)
        await ctx.send(f"✅ Welcome channel set to {channel.mention}")

    # -------------------------
    # Set goodbye channel
    # -------------------------
    @commands.command(name="setgoodbyechannel", help="Set the channel for goodbye messages.")
    @commands.has_permissions(administrator=True)
    async def set_goodbye_channel(self, ctx, channel: discord.TextChannel):
        cfg = self.get_guild_cfg(ctx.guild.id)
        cfg["goodbye_channel"] = channel.id
        save_config(self.config)
        await ctx.send(f"✅ Goodbye channel set to {channel.mention}")

    # -------------------------
    # Set welcome message
    # -------------------------
    @commands.command(name="setwelcomemsg", help="Set the welcome message.")
    @commands.has_permissions(administrator=True)
    async def set_welcome_message(self, ctx, *, message: str):
        cfg = self.get_guild_cfg(ctx.guild.id)
        cfg["welcome_message"] = message
        save_config(self.config)
        await ctx.send(f"✅ Welcome message set:\n`{message}`")

async def setup(bot):
    await bot.add_cog(ServerSettings(bot))
