import discord
from discord.ext import commands
from pathlib import Path
import json

DATA_DIR = Path("data")
SETTINGS_FILE = DATA_DIR / "server_roles.json"

DATA_DIR.mkdir(exist_ok=True)
if not SETTINGS_FILE.exists():
    SETTINGS_FILE.write_text("{}")


class Admin(commands.Cog):
    category = "Admin"
    """Admin-level server configuration commands"""
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.config = self.load_config()

    # -------------------------
    # CONFIG HANDLING
    # -------------------------
    def load_config(self) -> dict:
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {}

    def save_config(self):
        SETTINGS_FILE.write_text(json.dumps(self.config, indent=4))

    def get_guild_config(self, guild_id: int) -> dict:
        return self.config.setdefault(
            str(guild_id),
            {"admin_roles": [], "mod_roles": [], "help_roles": []},
        )

    # -------------------------
    # ADMIN COMMANDS
    # -------------------------
    @commands.command(name="setadminrole")
    @commands.has_permissions(administrator=True)
    async def set_admin_role(self, ctx: commands.Context, role: discord.Role):
        """Set the Admin role for this server."""
        cfg = self.get_guild_config(ctx.guild.id)  # type: ignore

        if role.id in cfg["admin_roles"]:
            await ctx.send("⚠️ This role is already set as Admin.")
            return

        cfg["admin_roles"].append(role.id)
        self.save_config()

        await ctx.send(f"✅ Admin role added: {role.mention}")

    @commands.command(name="setmodrole")
    @commands.has_permissions(administrator=True)
    async def set_mod_role(self, ctx: commands.Context, role: discord.Role):
        """Set the Moderator role for this server."""
        cfg = self.get_guild_config(ctx.guild.id)  # type: ignore

        if role.id in cfg["mod_roles"]:
            await ctx.send("⚠️ This role is already set as Moderator.")
            return

        cfg["mod_roles"].append(role.id)
        self.save_config()

        await ctx.send(f"✅ Moderator role added: {role.mention}")

    @commands.command(name="sethelpaccess")
    @commands.has_permissions(administrator=True)
    async def set_help_access(self, ctx: commands.Context, role: discord.Role):
        """Restrict the help command to a specific role."""
        cfg = self.get_guild_config(ctx.guild.id)  # type: ignore

        if role.id in cfg["help_roles"]:
            await ctx.send("⚠️ This role already has help access.")
            return

        cfg["help_roles"].append(role.id)
        self.save_config()

        await ctx.send(f"📘 Help access granted to: {role.mention}")

    @commands.command(name="viewroles")
    @commands.has_permissions(administrator=True)
    async def view_roles(self, ctx: commands.Context):
        """View configured Admin/Mod/Help roles."""
        cfg = self.get_guild_config(ctx.guild.id)  # type: ignore

        def fmt(role_ids):
            roles = [ctx.guild.get_role(r) for r in role_ids]  # type: ignore
            return ", ".join(r.mention for r in roles if r) or "None"

        embed = discord.Embed(
            title="🛡️ Server Role Configuration",
            color=0x2ECC71,
        )
        embed.add_field(name="Admin Roles", value=fmt(cfg["admin_roles"]), inline=False)
        embed.add_field(name="Moderator Roles", value=fmt(cfg["mod_roles"]), inline=False)
        embed.add_field(name="Help Access Roles", value=fmt(cfg["help_roles"]), inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="resetroles")
    @commands.has_permissions(administrator=True)
    async def reset_roles(self, ctx: commands.Context):
        """Reset all role configuration for this server."""
        self.config.pop(str(ctx.guild.id), None)  # type: ignore
        self.save_config()
        await ctx.send("🔄 All role settings have been reset.")
    

    @commands.command(name="listxroles")
    async def list_roles(self, ctx):
        """Shows:
    Configured admin role
    Configured mod role."""
    
        # Fetch saved config for this guild
        guild_config = self.get_guild_config(ctx.guild.id)  # use your config method
        # Example: guild_config = {"admin_role": 123456, "mod_role": 654321}

        admin_role_id = guild_config.get("admin_role", 0)
        mod_role_id = guild_config.get("mod_role", 0)

        admin_role = ctx.guild.get_role(admin_role_id)
        mod_role = ctx.guild.get_role(mod_role_id)

        embed = discord.Embed(
            title="🔐 Server Roles",
            color=discord.Color.blurple()
    )
        embed.add_field(
            name="Admin Role",
            value=admin_role.mention if admin_role else "❌ Not set",
            inline=False
    )
        embed.add_field(
            name="Mod Role",
            value=mod_role.mention if mod_role else "❌ Not set",
            inline=False
    )
        await ctx.send(embed=embed)



async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
