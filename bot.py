import os
import discord
from discord.ext import commands
import config


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.reactions = True
intents.guilds = True


class MyBot(commands.Bot):
    async def setup_hook(self):

        # Load cogs
        for root, _, files in os.walk("cogs"):
            for file in files:
                if file.endswith(".py") and file != "__init__.py":
                    module = (
                        os.path.join(root, file)
                        .replace("\\", ".")
                        .replace("/", ".")[:-3]
                    )
                    try:
                        await self.load_extension(module)
                        print(f"[✅] Loaded {module}")
                    except Exception as e:
                        print(f"[❌] Failed to load {module}: {e}")


bot = MyBot(command_prefix=config.PREFIX, intents=intents)
bot.help_command = None


@bot.event
async def on_ready():
    print(f"✅ Bot is ready: {bot.user}")
    print(f"🌐 Server count: {len(bot.guilds)}")
    print(f"📌 Prefix: {config.PREFIX}")


@bot.event
async def on_command_error(ctx, error):
    error = getattr(error, "original", error)

    if isinstance(error, commands.CommandNotFound):
        return
    if isinstance(error, commands.MissingRequiredArgument):
        return await ctx.send(f"❌ Missing argument: {error.param.name}")
    if isinstance(error, commands.BadArgument):
        return await ctx.send("❌ Invalid input.")
    if isinstance(error, commands.CommandOnCooldown):
        return await ctx.send(f"❌ Cooldown. Try again in {error.retry_after:.1f}s.")
    if isinstance(error, discord.Forbidden):
        return await ctx.send("❌ I don't have permission to do that.")
    if isinstance(error, commands.CheckFailure):
        return await ctx.send("❌ You don't have permission.")

    print(f"Unhandled error: {type(error).__name__}: {error}")
    await ctx.send("⚠️ An unexpected error occurred.")


if __name__ == "__main__":
    if config.TOKEN:
        bot.run(config.TOKEN)
    else:
        print("❌ DISCORD_TOKEN not set")
