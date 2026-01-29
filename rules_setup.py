import discord
from discord.ext import commands


class RulesSetup(commands.Cog):
    category = "Owner"
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setuprules")
    @commands.has_permissions(manage_guild=True)
    async def setup_rules(self, ctx: commands.Context):
        """Post the full SX2 rules system (split, TL;DR, reaction agree)"""

        await ctx.send(
            "**📜 SX2 OFFICIAL — SERVER RULES**\n\n"
            "Welcome to **SX2 Official** 🎮🍿🎶\n"
            "SX2 is a community for **gaming**, **anime**, and **music** fans to chill, "
            "connect, and have fun.\n\n"
            "To keep the server safe, respectful, and enjoyable for everyone, all members "
            "must follow the rules below.\n"
            "Failure to comply may result in warnings, mutes, or bans.\n\n"
            "Please read carefully 👇"
        )

        await ctx.send(
            "**🤝 Be Respectful**\n"
            "• Treat all members with respect\n"
            "• No harassment, hate speech, discrimination, or personal attacks\n"
            "• Racism, sexism, homophobia, or threats = **zero tolerance**\n\n"
            "**💬 Use Channels Properly**\n"
            "• Keep conversations in the correct channels\n"
            "• No spamming, flooding, or excessive tagging\n"
            "• Don’t derail serious discussions\n\n"
            "**🚫 No NSFW or Illegal Content**\n"
            "• No NSFW, sexual, or explicit content\n"
            "• No illegal activities, piracy, or malicious links\n"
            "• Applies to messages, usernames, avatars, and links"
        )

        await ctx.send(
            "**🔔 No Spam or Self-Promotion**\n"
            "• No unsolicited ads, invites, or promotions\n"
            "• Self-promo only in designated channels (if available)\n"
            "• DM advertising is strictly prohibited\n\n"
            "**🛡️ Follow Discord ToS**\n"
            "• You must follow Discord’s Terms of Service & Community Guidelines\n"
            "• Ban evasion or alt accounts to avoid punishment are not allowed\n\n"
            "**🎭 Usernames & Profiles**\n"
            "• Offensive or inappropriate names or avatars are not allowed\n"
            "• Staff may request changes if needed"
        )

        await ctx.send(
            "**🎮 Gaming & Voice Chat Etiquette**\n"
            "• No mic spamming, soundboard abuse, or voice disruption\n"
            "• Respect others during games and voice sessions\n"
            "• Follow event-specific rules when participating\n\n"
            "**🧠 Moderator Decisions**\n"
            "• Staff decisions are final\n"
            "• If you have an issue, contact a moderator calmly and privately\n"
            "• Do not argue moderation actions in public channels\n\n"
            "**⚠️ Common Sense Applies**\n"
            "• Loopholes are not excuses\n"
            "• If something feels wrong, don’t do it\n"
            "• Staff may act in situations not explicitly listed"
        )

        await ctx.send(
            "**📌 TL;DR — QUICK RULES SUMMARY**\n\n"
            "• Be respectful\n"
            "• No hate, harassment, or NSFW\n"
            "• No spam or self-promo\n"
            "• Use correct channels\n"
            "• Follow Discord ToS\n"
            "• Respect staff decisions\n\n"
            "If you can follow these, you’ll fit right in at **SX2 Official** 💜"
        )

        agree_msg = await ctx.send(
            "**✅ RULES ACKNOWLEDGEMENT**\n\n"
            "By reacting with **✅** below, you confirm that:\n"
            "• You have read the rules\n"
            "• You understand them\n"
            "• You agree to follow them while in **SX2 Official**\n\n"
            "Failure to follow the rules may result in moderation action.\n\n"
            "**Game • Watch • Vibe** 🎮🍿🎶"
        )

        await agree_msg.add_reaction("✅")

        await ctx.send("✅ **Rules system successfully posted.**")

    @setup_rules.error
    async def setup_rules_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You need **Manage Server** permission to run this command.")


async def setup(bot):
    await bot.add_cog(RulesSetup(bot))
