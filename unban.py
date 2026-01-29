import discord
from discord.ext import commands
import config
from checks import mod_or_higher


class Unban(commands.Cog):
    category = "Moderation"

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.command(
        name="unban", help="Unban by user ID. Usage: !unban <user_id> [reason]"
    )
    @mod_or_higher()
    async def unban(
        self,
        ctx: commands.Context,
        user_id: int,
        *,
        reason: str = "No reason provided",
    ):
        if ctx.guild is None:
            return

        user = discord.Object(id=user_id)  # lightweight user reference

        try:
            await ctx.guild.unban(user, reason=f"{reason} (by {ctx.author})")
        except discord.NotFound:
            return await ctx.send("❌ That user isn’t banned (or wrong ID).")
        except discord.Forbidden:
            return await ctx.send("❌ I don’t have permission to unban users.")
        except discord.HTTPException:
            return await ctx.send("❌ Unban failed due to a Discord error.")

        await ctx.send(f"✅ Unbanned `<{user_id}>`.\nReason: {reason}")

        # Mod-log
        modlog_id = config.server_config.get_channel_id(
            ctx.guild.id, config.MOD_LOG_CHANNEL_ID_KEY
        )
        if modlog_id:
            channel = ctx.guild.get_channel(modlog_id)
            if isinstance(channel, discord.TextChannel):
                embed = discord.Embed(
                    title="User Unbanned", color=discord.Color.green()
                )
                embed.add_field(name="User ID", value=str(user_id), inline=False)
                embed.add_field(
                    name="By", value=f"{ctx.author} (`{ctx.author.id}`)", inline=False
                )
                embed.add_field(name="Reason", value=reason, inline=False)
                await channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Unban(bot))
