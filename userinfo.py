import discord
from discord.ext import commands
from typing import Optional
import datetime


class UserInfo(commands.Cog):
    category = "utilites"

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="userinfo", aliases=["ui", "whois"])
    async def userinfo(self, ctx, member: Optional[discord.Member] = None):
        """
        Show detailed user information.
        Usage: !userinfo @User or !userinfo
        """

        # Default to command author
        member = member or ctx.author

        # ---------- BASIC USER INFO ----------
        username = f"{member.name}#{member.discriminator}"
        nickname = member.nick if member.nick else "None"
        user_id = member.id

        created_at = member.created_at.strftime("%d %B %Y • %H:%M UTC")
        joined_at = (
            member.joined_at.strftime("%d %B %Y • %H:%M UTC")
            if member.joined_at
            else "Unknown"
        )

        # ---------- ROLES ----------
        roles = [r.mention for r in member.roles if r.name != "@everyone"]
        roles_display = ", ".join(roles) if roles else "None"
        highest_role = member.top_role.mention if member.top_role else "None"

        # ---------- STATUS ----------
        status_emojis = {
            discord.Status.online: "🟢 Online",
            discord.Status.idle: "🟡 Idle",
            discord.Status.dnd: "🔴 Do Not Disturb",
            discord.Status.offline: "⚫ Offline",
        }
        status = status_emojis.get(member.status, "⚫ Unknown")

        # ---------- ACTIVITY ----------
        activity = "None"
        if member.activities:
            for act in member.activities:
                if isinstance(act, discord.Spotify):
                    activity = f"🎵 Spotify — {act.title}"
                elif isinstance(act, discord.Game):
                    activity = f"🎮 Playing — {act.name}"
                elif isinstance(act, discord.Streaming):
                    activity = f"📺 Streaming — {act.name}"
                elif isinstance(act, discord.CustomActivity):
                    activity = act.name or "Custom Status"

        # ---------- EMBED ----------
        embed = discord.Embed(
            title="👤 User Information",
            color=0x5865F2,
            timestamp=datetime.datetime.now(datetime.UTC),
        )

        embed.set_thumbnail(url=member.display_avatar.url)

        # ===== USER INFO (TABLE STYLE) =====
        embed.add_field(
            name="📌 USER INFO",
            value=(
                f"**Username:** `{username}`\n"
                f"**Nickname:** `{nickname}`\n"
                f"**User ID:** `{user_id}`\n"
                f"**Account Created:** `{created_at}`"
            ),
            inline=False,
        )

        # ===== MEMBER INFO (TABLE STYLE) =====
        embed.add_field(
            name="📌 MEMBER INFO",
            value=(
                f"**Joined Server:** `{joined_at}`\n"
                f"**Status:** {status}\n"
                f"**Highest Role:** {highest_role}\n"
                f"**Activity:** `{activity}`"
            ),
            inline=False,
        )

        # ===== ROLES =====
        embed.add_field(
            name=f"🎭 Roles ({len(roles)})",
            value=roles_display,
            inline=False,
        )

        # Footer
        embed.set_footer(
            text=f"Requested by {ctx.author}",
            icon_url=ctx.author.display_avatar.url,
        )

        await ctx.send(embed=embed)

    @userinfo.error
    async def userinfo_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send("❌ Invalid user mentioned.")
        else:
            print(f"[UserInfo Error] {error}")


async def setup(bot):
    await bot.add_cog(UserInfo(bot))
