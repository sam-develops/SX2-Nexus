import discord
from discord.ext import commands
import config
from checks import mod_or_higher


class Ban(commands.Cog):
    category = "Moderation"

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(name="ban", help="Ban a member. Usage: !ban @user [reason]")
    @mod_or_higher()
    async def ban(
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

        # If they are still in the guild, we can do hierarchy checks
        if member is not None:
            if member.id == ctx.author.id:
                return await ctx.send("❌ You can’t ban yourself.")

            me = ctx.guild.me
            if me and member.top_role >= me.top_role:
                return await ctx.send(
                    "❌ I can’t ban that member (role hierarchy). Move my role higher."
                )

            if isinstance(ctx.author, discord.Member):
                if (
                    member.top_role >= ctx.author.top_role
                    and ctx.author != ctx.guild.owner
                ):
                    return await ctx.send(
                        "❌ You can’t ban someone with an equal/higher role than you."
                    )

            # Try DM before ban
            try:
                await member.send(
                    f"You were banned from **{ctx.guild.name}**.\nReason: {reason}"
                )
            except (discord.Forbidden, discord.HTTPException):
                pass

        # Ban (works for Member or User)
        try:
            await ctx.guild.ban(
                target, reason=f"{reason} (by {ctx.author})", delete_message_days=0
            )
        except discord.Forbidden:
            return await ctx.send("❌ I don’t have permission to ban members.")
        except discord.HTTPException:
            return await ctx.send("❌ Ban failed due to a Discord error.")

        await ctx.send(f"✅ Banned **{target}**.\nReason: {reason}")

        # Mod-log
        modlog_id = config.server_config.get_channel_id(
            ctx.guild.id, config.MOD_LOG_CHANNEL_ID_KEY
        )
        if modlog_id:
            channel = ctx.guild.get_channel(modlog_id)
            if isinstance(channel, discord.TextChannel):
                embed = discord.Embed(title="Member Banned", color=discord.Color.red())
                embed.add_field(
                    name="User", value=f"{target} (`{target.id}`)", inline=False
                )
                embed.add_field(
                    name="By", value=f"{ctx.author} (`{ctx.author.id}`)", inline=False
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Ban(bot))
