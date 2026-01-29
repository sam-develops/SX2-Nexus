import discord
from discord.ext import commands
import config
from checks import mod_or_higher


class Kick(commands.Cog):
    category = "Moderation"

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="kick", help="Kick a member. Usage: !kick @user [reason]")
    @mod_or_higher()
    async def kick(
        self,
        ctx: commands.Context,
        target: discord.Member | discord.User,
        *,
        reason: str = "No reason provided",
    ):
        if ctx.guild is None:
            return

        member = (
            target
            if isinstance(target, discord.Member)
            else ctx.guild.get_member(target.id)
        )
        if member is None:
            return await ctx.send("❌ That user is not in this server.")

        # Prevent kicking yourself or the bot
        if member.id == ctx.author.id:
            return await ctx.send("❌ You can’t kick yourself.")
        if ctx.guild.me and member.id == ctx.guild.me.id:
            return await ctx.send("❌ I can’t kick myself.")

        # Role hierarchy checks
        if isinstance(ctx.author, discord.Member):
            if member.top_role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                return await ctx.send(
                    "❌ You can’t kick someone with an equal/higher role than you."
                )

        if ctx.guild.me and member.top_role >= ctx.guild.me.top_role:
            return await ctx.send(
                "❌ I can’t kick that member (role hierarchy). Move my role higher."
            )

        # Try DM before kick
        try:
            await member.send(
                f"You were kicked from **{ctx.guild.name}**.\nReason: {reason}"
            )
        except (discord.Forbidden, discord.HTTPException):
            pass

        # Kick
        try:
            await member.kick(reason=f"{reason} (by {ctx.author})")
        except discord.Forbidden:
            return await ctx.send("❌ I don’t have permission to kick members.")
        except discord.HTTPException:
            return await ctx.send("❌ Kick failed due to a Discord error.")
        await ctx.send(f"✅ Kicked **{member}**.\nReason: {reason}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Kick(bot))
