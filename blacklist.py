# cogs/admin/blacklist.py
import discord
from discord.ext import commands
from pathlib import Path
import json

DATA_DIR = Path("data")
BLACKLIST_FILE = DATA_DIR / "blacklist.json"
DATA_DIR.mkdir(exist_ok=True)
if not BLACKLIST_FILE.exists():
    BLACKLIST_FILE.write_text("{}")  # Empty JSON object

class Blacklist(commands.Cog):
    category = "Owner"
    """Manage Blacklist / Whitelist users per server."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.blacklist_data = self.load_blacklist()

    # -------------------------
    # File Handling
    # -------------------------
    def load_blacklist(self):
        try:
            return json.loads(BLACKLIST_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_blacklist(self):
        BLACKLIST_FILE.write_text(json.dumps(self.blacklist_data, indent=4))

    def get_guild_blacklist(self, guild_id: int):
        return self.blacklist_data.setdefault(str(guild_id), {"blacklist": [], "whitelist": []})

    # -------------------------
    # Blacklist Commands
    # -------------------------
    @commands.command(name="blacklist", help="Add a user to the blacklist (Admin only).")
    @commands.has_permissions(administrator=True)
    async def blacklist_user(self, ctx, member: discord.Member):
        guild_data = self.get_guild_blacklist(ctx.guild.id)
        if member.id in guild_data["blacklist"]:
            await ctx.send(f"❌ {member.mention} is already blacklisted.")
            return

        guild_data["blacklist"].append(member.id)
        if member.id in guild_data["whitelist"]:
            guild_data["whitelist"].remove(member.id)
        self.save_blacklist()
        await ctx.send(f"✅ {member.mention} has been **blacklisted**.")

    @commands.command(name="unblacklist", help="Remove a user from the blacklist (Admin only).")
    @commands.has_permissions(administrator=True)
    async def unblacklist_user(self, ctx, member: discord.Member):
        guild_data = self.get_guild_blacklist(ctx.guild.id)
        if member.id not in guild_data["blacklist"]:
            await ctx.send(f"❌ {member.mention} is not blacklisted.")
            return

        guild_data["blacklist"].remove(member.id)
        self.save_blacklist()
        await ctx.send(f"✅ {member.mention} has been **removed from the blacklist**.")

    # -------------------------
    # Whitelist Commands
    # -------------------------
    @commands.command(name="whitelist", help="Add a user to the whitelist (Admin only).")
    @commands.has_permissions(administrator=True)
    async def whitelist_user(self, ctx, member: discord.Member):
        guild_data = self.get_guild_blacklist(ctx.guild.id)
        if member.id in guild_data["whitelist"]:
            await ctx.send(f"❌ {member.mention} is already whitelisted.")
            return

        guild_data["whitelist"].append(member.id)
        if member.id in guild_data["blacklist"]:
            guild_data["blacklist"].remove(member.id)
        self.save_blacklist()
        await ctx.send(f"✅ {member.mention} has been **whitelisted**.")

    @commands.command(name="unwhitelist", help="Remove a user from the whitelist (Admin only).")
    @commands.has_permissions(administrator=True)
    async def unwhitelist_user(self, ctx, member: discord.Member):
        guild_data = self.get_guild_blacklist(ctx.guild.id)
        if member.id not in guild_data["whitelist"]:
            await ctx.send(f"❌ {member.mention} is not whitelisted.")
            return

        guild_data["whitelist"].remove(member.id)
        self.save_blacklist()
        await ctx.send(f"✅ {member.mention} has been **removed from the whitelist**.")

    # -------------------------
    # List Blacklist / Whitelist
    # -------------------------
    @commands.command(name="listblacklist", help="Show all blacklisted users in this server.")
    @commands.has_permissions(administrator=True)
    async def list_blacklist(self, ctx):
        guild_data = self.get_guild_blacklist(ctx.guild.id)
        if not guild_data["blacklist"]:
            await ctx.send("✅ No users are blacklisted.")
            return

        mentions = [f"<@{uid}>" for uid in guild_data["blacklist"]]
        embed = discord.Embed(
            title="🚫 Blacklisted Users",
            description="\n".join(mentions),
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    @commands.command(name="listwhitelist", help="Show all whitelisted users in this server.")
    @commands.has_permissions(administrator=True)
    async def list_whitelist(self, ctx):
        guild_data = self.get_guild_blacklist(ctx.guild.id)
        if not guild_data["whitelist"]:
            await ctx.send("✅ No users are whitelisted.")
            return

        mentions = [f"<@{uid}>" for uid in guild_data["whitelist"]]
        embed = discord.Embed(
            title="✅ Whitelisted Users",
            description="\n".join(mentions),
            color=discord.Color.green()
        )
        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Blacklist(bot))
