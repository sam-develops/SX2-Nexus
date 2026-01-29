import discord
from discord.ext import commands

class Welcome(commands.Cog):
    category = "Owner"
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="welcome")
    @commands.has_permissions(manage_guild=True)
    async def welcome(self, ctx: commands.Context):
        """Send the SX2 Official welcome embed"""

        embed = discord.Embed(
            title="🎮 WELCOME TO SX2 OFFICIAL 🍿🎶",
            description=(
                "**Welcome to SX2 Official** — a community built for "
                "**gamers**, **anime lovers**, and **music fans** to connect, chill, "
                "and have fun together.\n\n"
                "You’re officially part of the squad now — let’s get you started 🚀"
            ),
            color=discord.Color.purple()
        )

        embed.add_field(
            name="📜 Start Here",
            value=(
                "Before jumping into chat, please take a moment to read **#📜-server-rules**.\n"
                "It helps keep SX2 friendly, respectful, and fun for everyone."
            ),
            inline=False
        )

        embed.add_field(
            name="🎭 Choose Your Roles",
            value=(
                "Head over to **#🗝️-roles** to pick your gaming, anime, and notification roles.\n"
                "Roles unlock channels and personalise your experience."
            ),
            inline=False
        )

        embed.add_field(
            name="👋 Introduce Yourself",
            value=(
                "Say hello in **#👤⤬introduction**!\n"
                "Let us know what games you play, your favourite anime, "
                "or what music you vibe with 🎧"
            ),
            inline=False
        )

        embed.add_field(
            name="💬 Join the Conversation",
            value=(
                "Jump into **# 💬⥐general**, gaming categories based on your platforms, #🍿・anime-talk, "
                "or music chats.\n"
                "There’s always something going on in SX2."
            ),
            inline=False
        )

        embed.add_field(
            name="🔔 Events & Updates",
            value=(
                "Want to stay in the loop?\n"
                "Opt into event & giveaway notifications so you never miss out 🎉"
            ),
            inline=False
        )

        embed.add_field(
            name="🆘 Need Help?",
            value=(
                "Visit **# ⛑️x-help-desk** or tag a @moderator — we’ve got you covered 💜"
            ),
            inline=False
        )

        embed.set_footer(text="SX2 Official • Game • Watch • Vibe")

        await ctx.send(embed=embed)

    @welcome.error
    async def welcome_error(self, ctx: commands.Context, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You don’t have permission to use this command.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
