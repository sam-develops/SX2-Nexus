# bot.py
# ===============================
# Discord Bot - Tiered Moderation System
# ===============================

import discord
from discord.ext import commands
import config
from datetime import timedelta

# -------------------------
# Bot Setup
# -------------------------
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)

# -------------------------
# Custom Permission Checks
# -------------------------


def is_owner():
    """Only the server owner can use this."""

    async def predicate(ctx):
        return ctx.author == ctx.guild.owner

    return commands.check(predicate)


def is_admin_or_owner():
    """Admin or Owner only."""

    async def predicate(ctx):
        if ctx.author == ctx.guild.owner:
            return True
        return any(role.name == config.ADMIN_ROLE for role in ctx.author.roles)

    return commands.check(predicate)


def is_moderator_or_higher():
    """Moderator, Admin, or Owner."""

    async def predicate(ctx):
        if ctx.author == ctx.guild.owner:
            return True
        if any(role.name == config.ADMIN_ROLE for role in ctx.author.roles):
            return True
        return any(role.name == config.MODERATOR_ROLE for role in ctx.author.roles)

    return commands.check(predicate)


# -------------------------
# Global Error Handler
# -------------------------
@bot.event
async def on_command_error(ctx, error):
    """Handle all command errors with user-friendly messages."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Missing required argument. Try: `!clear 5`")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("❌ Invalid argument. Did you mention a user? (e.g., @user)")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.CheckFailure):
        cmd = ctx.command.name
        author = ctx.author
        guild = ctx.guild

        # Check who is trying to run it
        if author == guild.owner:
            await ctx.send(
                f"❌ This command requires higher privileges. Try again as Admin or Moderator."
            )
        elif any(role.name == config.ADMIN_ROLE for role in author.roles):
            await ctx.send(f"❌ talk to the owner to use `{cmd}`.")
        elif any(role.name == config.MODERATOR_ROLE for role in author.roles):
            await ctx.send(f"❌ You need the Admin role to use `{cmd}`. command")
        else:
            await ctx.send(f"❌ You need the Moderator role to use `{cmd}`. command")
    else:
        print(f"Unhandled error: {error}")
        await ctx.send("❌ An unexpected error occurred. Please report to the owner.")


# -------------------------
# Commands (Tiered Access)
# -------------------------

# === MODERATOR-ONLY COMMANDS ===
# Can be used by Moderator, Admin, or Owner


@bot.command(name="clear")
@is_moderator_or_higher()
async def clear_messages(ctx, amount: int = 5):
    """Delete messages (Moderator+). Usage: !clear 5"""
    if amount > 100:
        await ctx.send("Cannot delete more than 100 messages at once!")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(
        f"Deleted {len(deleted)-1} messages by {ctx.author} !", delete_after=3
    )


@bot.command(name="timeout")
@is_moderator_or_higher()
async def timeout_member(ctx, member: discord.Member, minutes: int = 10, *, reason: str = None):  # type: ignore
    """Timeout a member. Usage: !timeout @user 5 spamming"""
    try:
        duration = timedelta(minutes=minutes)
        await member.edit(
            timed_out_until=discord.utils.utcnow() + duration, reason=reason
        )
        await ctx.send(f"✅ Timed out {member.mention} for {minutes} minute(s).")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to timeout that member.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


@bot.command(name="softban")
@is_moderator_or_higher()
async def softban_member(ctx, member: discord.Member, *, reason: str = None):  # type: ignore
    """Softban: ban then unban to delete messages. Usage: !softban @user cleanup"""
    try:
        await ctx.guild.ban(member, reason=reason, delete_message_days=7)
        await ctx.guild.unban(member, reason="Softban auto-unban")
        await ctx.send(f"✅ Softbanned {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to softban that member.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


# === ADMIN-ONLY COMMANDS ===
# Can be used by Admin or Owner


@bot.command(name="kick")
@is_admin_or_owner()
async def kick_member(ctx, member: discord.Member, *, reason: str = None):  # type: ignore
    """Kick a member (Admin/Owner only). Usage: !kick @user spam"""
    try:
        await member.kick(reason=reason)
        await ctx.send(f"✅ Kicked {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to kick that member.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


@bot.command(name="ban")
@is_admin_or_owner()
async def ban_member(ctx, member: discord.Member, *, reason: str = None):  # type: ignore
    """Ban a member (Admin/Owner only). Usage: !ban @user spam"""
    try:
        await member.ban(reason=reason)
        await ctx.send(f"✅ Banned {member.mention}.")
    except discord.Forbidden:
        await ctx.send("❌ I don't have permission to ban that member.")
    except Exception as e:
        await ctx.send(f"❌ Error: {e}")


# === OWNER-ONLY COMMANDS ===
# Only the server owner can use these


@bot.command(name="shutdown")
@is_owner()
async def shutdown_bot(ctx):
    """Shut the bot down (Owner only)."""
    await ctx.send("Shutting down... Bye! 👋")
    await bot.close()


# -------------------------
# Welcome Event
# -------------------------
@bot.event
async def on_member_join(member):
    guild = member.guild

    # Auto-role
    if config.AUTO_ROLE:
        role = discord.utils.get(guild.roles, name=config.AUTO_ROLE)
        if role:
            try:
                await member.add_roles(role, reason="Auto role on join")
            except discord.Forbidden:
                pass

    # Welcome message in channel
    if config.WELCOME_IN_CHANNEL:
        welcome_channel = discord.utils.get(
            guild.text_channels, name=config.WELCOME_CHANNEL
        )
        if welcome_channel:
            await welcome_channel.send(
                f"Welcome to {guild.name}, {member.mention}! Please read the rules."
            )

    # DM welcome
    if config.WELCOME_DM:
        try:
            await member.send(f"Welcome to **{guild.name}**! Check out <#{welcome_channel.id}> and enjoy your stay!")  # type: ignore
        except Exception:
            pass

    # Log join
    mod_channel = discord.utils.get(guild.text_channels, name=config.MOD_LOG_CHANNEL)
    if mod_channel:
        await mod_channel.send(f"📥 {member} joined the server.")


# -------------------------
# Bot Ready
# -------------------------
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    print(f"🌐 Server count: {len(bot.guilds)}")
    print(f"📌 Prefix: {config.PREFIX}")


# -------------------------
# Run the Bot
# -------------------------
if __name__ == "__main__":
    bot.run(config.TOKEN)  # type: ignore # ← Add your bot token here!
