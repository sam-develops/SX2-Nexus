import discord
from discord.ext import commands

import config
from checks import mod_or_higher


class Clear(commands.Cog):
    category = "Moderation"
    """Clear messages from a channel or a specific user."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def _log_action(
        self,
        guild: discord.Guild,
        *,
        actor: discord.Member,
        channel: discord.TextChannel,
        action: str,
        details: str,
    ):
        modlog_id = config.server_config.get_channel_id(
            guild.id, config.MOD_LOG_CHANNEL_ID_KEY
        )
        if not modlog_id:
            return

        modlog = guild.get_channel(modlog_id)
        if not isinstance(modlog, discord.TextChannel):
            return

        embed = discord.Embed(
            title=f"📋 Moderation: {action}",
            description=details,
            color=0xED4245,  # red-ish
        )
        embed.add_field(name="Moderator", value=f"{actor} ({actor.id})", inline=False)
        embed.add_field(
            name="Channel", value=f"{channel.mention} ({channel.id})", inline=False
        )
        embed.set_footer(text=f"Guild: {guild.name} • ID: {guild.id}")

        try:
            await modlog.send(embed=embed)
        except discord.Forbidden:
            pass
        except discord.HTTPException:
            pass

    @commands.guild_only()
    @commands.command(
        name="clear",
        help="Clear messages. Usage: !clear [amount] OR !clear @user [amount]",
    )
    @mod_or_higher()
    async def clear(
        self,
        ctx: commands.Context,
        amount_or_user: int | discord.Member | None = None,
        amount: int = 10,
    ):
        if ctx.guild is None or not isinstance(ctx.channel, discord.TextChannel):
            return

        user: discord.Member | None = None

        # Allow both:
        #   !clear 10
        #   !clear @user 10
        if isinstance(amount_or_user, int):
            amount = amount_or_user
        elif isinstance(amount_or_user, discord.Member):
            user = amount_or_user

        if amount < 1:
            return await ctx.send("❌ You must delete at least 1 message.")
        if amount > 200:
            return await ctx.send("❌ Max allowed is 200 messages at a time.")

        def check(m: discord.Message):
            return (m.author.id == user.id) if user else True

        try:
            deleted = await ctx.channel.purge(
                limit=amount, check=check, reason=f"Clear used by {ctx.author}"
            )
        except discord.Forbidden:
            return await ctx.send("❌ I don't have permission to delete messages here.")
        except discord.HTTPException:
            return await ctx.send("❌ Failed to delete messages (Discord error).")

        target = f"from **{user}**" if user else "messages"
        await ctx.send(f"🧹 Deleted **{len(deleted)}** {target}.", delete_after=5)

        await self._log_action(
            ctx.guild,
            actor=ctx.author,  # type: ignore (discord.py types)
            channel=ctx.channel,
            action="Clear",
            details=f"Deleted **{len(deleted)}** messages {('from ' + user.mention) if user else ''}",
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Clear(bot))
