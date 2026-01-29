import discord
from discord.ext import commands
from discord import ui
import json
import os

CONFIG_PATH = "data/welcome_config.json"


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_PATH, "w") as f:
        json.dump(data, f, indent=4)


class ChannelSelect(ui.Select):
    category = "Owner"
    def __init__(self, placeholder, key, guild):
        self.key = key
        options = [
            discord.SelectOption(label=ch.name, value=str(ch.id))
            for ch in guild.text_channels
        ]
        super().__init__(
            placeholder=placeholder,
            options=options[:25],  # Discord limit
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        config = load_config()
        guild_id = str(interaction.guild.id) # type: ignore

        if guild_id not in config:
            config[guild_id] = {}

        config[guild_id][self.key] = int(self.values[0])
        save_config(config)

        await interaction.response.send_message(
            f"✅ **Channel saved successfully.**",
            ephemeral=True
        )


class ChannelSelectView(ui.View):
    def __init__(self, guild, key, placeholder):
        super().__init__(timeout=60)
        self.add_item(ChannelSelect(placeholder, key, guild))


class WelcomeSetupView(ui.View):
    def __init__(self, guild):
        super().__init__(timeout=None)
        self.guild = guild

    @ui.button(label="📜 Set Rules Channel", style=discord.ButtonStyle.secondary)
    async def rules(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(
            "Select the **Rules channel**:",
            view=ChannelSelectView(self.guild, "rules_channel", "Choose rules channel"),
            ephemeral=True
        )

    @ui.button(label="🎭 Set Roles Channel", style=discord.ButtonStyle.secondary)
    async def roles(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(
            "Select the **Roles channel**:",
            view=ChannelSelectView(self.guild, "roles_channel", "Choose roles channel"),
            ephemeral=True
        )

    @ui.button(label="👋 Set Introductions Channel", style=discord.ButtonStyle.secondary)
    async def intro(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(
            "Select the **Introductions channel**:",
            view=ChannelSelectView(self.guild, "intro_channel", "Choose introductions channel"),
            ephemeral=True
        )

    @ui.button(label="📢 Set Welcome Channel", style=discord.ButtonStyle.success)
    async def welcome(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.send_message(
            "Select the **Welcome channel**:",
            view=ChannelSelectView(self.guild, "welcome_channel", "Choose welcome channel"),
            ephemeral=True
        )

    @ui.button(label="🚀 Post Welcome Message", style=discord.ButtonStyle.primary)
    async def post(self, interaction: discord.Interaction, button: ui.Button):
        config = load_config()
        guild_id = str(self.guild.id)

        if guild_id not in config or "welcome_channel" not in config[guild_id]:
            await interaction.response.send_message(
                "❌ Welcome channel not configured yet.",
                ephemeral=True
            )
            return

        ch = self.guild.get_channel(config[guild_id]["welcome_channel"])

        embed = discord.Embed(
            title="🎮 Welcome to SX2 Official 🍿🎶",
            description=(
                "Welcome to **SX2 Official** — a community for **gaming**, "
                "**anime**, and **music** lovers.\n\n"
                "Follow the steps below to get started 🚀"
            ),
            color=discord.Color.from_rgb(138, 43, 226)
        )

        embed.add_field(
            name="📜 Read the Rules",
            value=f"Please read <#{config[guild_id].get('rules_channel', 0)}> before chatting.",
            inline=False
        )

        embed.add_field(
            name="🎭 Choose Your Roles",
            value=f"Pick your roles in <#{config[guild_id].get('roles_channel', 0)}>.",
            inline=False
        )

        embed.add_field(
            name="👋 Introduce Yourself",
            value=f"Say hello in <#{config[guild_id].get('intro_channel', 0)}>.",
            inline=False
        )

        embed.add_field(
            name="💬 Join the Community",
            value="Jump into chats, voice channels, and events.",
            inline=False
        )

        embed.set_footer(text="SX2 Official • Powered by SX2 Nexus")

        await ch.send(embed=embed)
        await interaction.response.send_message("✅ Welcome message posted.", ephemeral=True)


class WelcomeSetup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="setupwelcome")
    @commands.has_permissions(manage_guild=True)
    async def setup_welcome(self, ctx):
        embed = discord.Embed(
            title="⚙️ SX2 Welcome Setup",
            description=(
                "Use the buttons below to configure the **welcome system**.\n\n"
                "This setup works like **MEE6 / Dyno** and stores settings automatically."
            ),
            color=discord.Color.from_rgb(138, 43, 226)
        )
        embed.set_footer(text="SX2 Nexus • Welcome Configuration")

        await ctx.send(embed=embed, view=WelcomeSetupView(ctx.guild))


async def setup(bot):
    await bot.add_cog(WelcomeSetup(bot))
