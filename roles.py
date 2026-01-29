import discord
from discord.ext import commands
import asyncio
import json
import os
from typing import Dict

DATA_DIR = "data"
ROLES_FILE = os.path.join(DATA_DIR, "reaction_roles.json")
os.makedirs(DATA_DIR, exist_ok=True)
if not os.path.exists(ROLES_FILE):
    with open(ROLES_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=4)

# Roles that should NOT be self-assignable
RESTRICTED = {"Admin", "Moderator", "Owner", "SX2 Nexus"}

# The list of role NAMES you want to offer for self-assignment.
# Modify this list to match your server role names (case-sensitive).
AVAILABLE_ROLES = [
    "Gamer",
    "Legend",
    "Verified",
    "Member",
    "Xbox",
    "PS5",
    "PC",
    "Valorant",
    "otaku",
    "Server Booster"
]

class RoleSelector(commands.Cog):
    category = "Owner"
    def __init__(self, bot):
        self.bot = bot
        self.role_mapping: Dict[str, str] = self.load_roles()  # emoji_str -> role_name
        self.message_id_map: Dict[str, int] = {}  # guild_id -> message_id (optional)

    def load_roles(self) -> Dict[str, str]:
        try:
            with open(ROLES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def save_roles(self):
        try:
            with open(ROLES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.role_mapping, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[❌] Failed to save role mappings: {e}")

    @commands.command(name="setuproles")
    @commands.has_permissions(administrator=True)
    async def setup_roles(self, ctx):
        """
        Interactive setup:
        Prompts admin to provide an emoji for each role in AVAILABLE_ROLES.
        After collection, sends the role-selection message and adds reactions.
        """
        def check_author(m):
            return m.author == ctx.author and m.channel == ctx.channel

        await ctx.send(
            "🎯 Starting interactive role setup.\n"
            "You will be asked to send ONE emoji for each role listed.\n"
            "To skip a role, type `skip`.\n"
            "To cancel setup, type `cancel`.\n\n"
            "Please ensure the bot has Manage Emojis (for custom emojis) and Manage Roles (to assign roles)."
        )

        collected_mapping = {}
        for role_name in AVAILABLE_ROLES:
            if role_name in RESTRICTED:
                continue  # ensure restricted roles never get added

            # Check that role exists on the guild
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                await ctx.send(f"⚠️ Role `{role_name}` not found in this server. Skipping.")
                await asyncio.sleep(0.5)
                continue

            await ctx.send(f"Please send the emoji to use for the role **{role_name}** (or `skip` / `cancel`):")

            try:
                msg = await self.bot.wait_for("message", timeout=120.0, check=check_author)
            except asyncio.TimeoutError:
                await ctx.send("⏰ Setup timed out. Run `!setuproles` again when ready.")
                return

            content = msg.content.strip()
            if content.lower() == "cancel":
                await ctx.send("❌ Setup cancelled.")
                return
            if content.lower() == "skip":
                await ctx.send(f"⏭️ Skipped `{role_name}`.")
                await asyncio.sleep(0.3)
                continue

            # Validate emoji: accept unicode or custom emoji like <a:name:id> or <:name:id>
            emoji_str = None
            # If message has attachments or embeds we ignore — expect plain emoji text or actual custom emoji in content
            if msg.raw_mentions or msg.mentions:
                # not relevant
                pass

            # If user pasted a custom emoji, Discord displays it in content as <emoji>
            # We'll accept content directly, but ensure it can be added as a reaction
            try:
                # Try adding and removing reaction on the bot's behalf to validate emoji
                test_message = await ctx.send("Testing emoji...")
                await test_message.add_reaction(content)
                await test_message.clear_reactions()
                await test_message.delete()
                emoji_str = content
            except Exception:
                await ctx.send("❌ That doesn't look like a valid emoji I can react with. Please send a valid emoji or type `skip`.")
                # give one more chance
                try:
                    msg2 = await self.bot.wait_for("message", timeout=60.0, check=check_author)
                except asyncio.TimeoutError:
                    await ctx.send("⏰ Timeout. Run the command again to continue setup.")
                    return
                content2 = msg2.content.strip()
                if content2.lower() in ("cancel", "skip"):
                    if content2.lower() == "cancel":
                        await ctx.send("❌ Setup cancelled.")
                        return
                    else:
                        await ctx.send(f"⏭️ Skipped `{role_name}`.")
                        continue
                try:
                    test_message = await ctx.send("Testing emoji...")
                    await test_message.add_reaction(content2)
                    await test_message.clear_reactions()
                    await test_message.delete()
                    emoji_str = content2
                except Exception:
                    await ctx.send("❌ Still invalid. Skipping this role.")
                    continue

            # Ensure no duplicate emoji mapping
            if emoji_str in collected_mapping:
                await ctx.send("⚠️ That emoji is already assigned to another role in this setup. Skipping.")
                continue

            collected_mapping[emoji_str] = role_name
            await ctx.send(f"✅ Mapped {emoji_str} → `{role_name}`")
            await asyncio.sleep(0.3)

        if not collected_mapping:
            await ctx.send("⚠️ No role mappings were collected. Setup aborted.")
            return

        # Save the mappings under this guild id to allow different servers to have different mappings
        guild_key = str(ctx.guild.id)
        # load full file, keep other guilds' mappings intact
        try:
            with open(ROLES_FILE, "r", encoding="utf-8") as f:
                all_data = json.load(f)
        except Exception:
            all_data = {}

        all_data[guild_key] = collected_mapping
        with open(ROLES_FILE, "w", encoding="utf-8") as f:
            json.dump(all_data, f, indent=4, ensure_ascii=False)

        # Build and send the role selection message
        embed_lines = []
        for emoji, rname in collected_mapping.items():
            embed_lines.append(f"{emoji} → `{rname}`")
        embed_desc = "\n".join(embed_lines)

        embed = discord.Embed(
            title="🎯 Select Your Roles",
            description=(
                "Click an emoji below to assign or remove that role.\n\n"
                f"{embed_desc}\n\n"
                "⚠️ Admin/Mod/Owner/SX2 Nexus are not available here."
            ),
            color=0x5865F2
        )

        message = await ctx.send(embed=embed)
        # Add reactions
        for emoji in collected_mapping.keys():
            try:
                await message.add_reaction(emoji)
            except Exception:
                # If adding reaction fails for a custom emoji (maybe from another guild), just continue
                print(f"Failed to add reaction {emoji} on guild {ctx.guild.id}")

        await ctx.send("✅ Reaction role message created.")

        # Update in-memory mapping for this guild
        self.role_mapping[str(ctx.guild.id)] = collected_mapping # type: ignore

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        # Only handle guilds
        if payload.guild_id is None:
            return

        # Ignore the bot itself
        if payload.user_id == self.bot.user.id:
            return

        guild_id = str(payload.guild_id)
        try:
            with open(ROLES_FILE, "r", encoding="utf-8") as f:
                all_data = json.load(f)
        except Exception:
            all_data = {}

        guild_map = all_data.get(guild_id, {})
        emoji = str(payload.emoji)

        role_name = guild_map.get(emoji)
        if not role_name:
            return

        # extra safety: block restricted roles
        if role_name in RESTRICTED:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            print(f"[⚠️] Role {role_name} not found in guild {guild_id}")
            return

        member = guild.get_member(payload.user_id)
        if not member:
            try:
                member = await guild.fetch_member(payload.user_id)
            except Exception:
                return

        try:
            await member.add_roles(role, reason="Reaction role add")
            print(f"[+] Assigned {role_name} to {member.display_name}")
        except Exception as e:
            print(f"[❌] Could not add role: {e}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        if payload.guild_id is None:
            return
        if payload.user_id == self.bot.user.id:
            return

        guild_id = str(payload.guild_id)
        try:
            with open(ROLES_FILE, "r", encoding="utf-8") as f:
                all_data = json.load(f)
        except Exception:
            all_data = {}

        guild_map = all_data.get(guild_id, {})
        emoji = str(payload.emoji)

        role_name = guild_map.get(emoji)
        if not role_name:
            return

        if role_name in RESTRICTED:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        role = discord.utils.get(guild.roles, name=role_name)
        if not role:
            print(f"[⚠️] Role {role_name} not found in guild {guild_id}")
            return

        member = guild.get_member(payload.user_id)
        if not member:
            try:
                member = await guild.fetch_member(payload.user_id)
            except Exception:
                return

        try:
            await member.remove_roles(role, reason="Reaction role remove")
            print(f"[-] Removed {role_name} from {member.display_name}")
        except Exception as e:
            print(f"[❌] Could not remove role: {e}")

async def setup(bot):
    await bot.add_cog(RoleSelector(bot))
