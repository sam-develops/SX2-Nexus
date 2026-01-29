import discord
from discord.ext import commands
import config
from checks import admin_or_owner
from checks import mod_or_higher


class Setup(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.guild_only()
    @commands.group(name="setup", invoke_without_command=True)
    @admin_or_owner()
    async def setup_group(self, ctx: commands.Context):
        await ctx.send(
            "Setup commands:\n"
            "`!setup setrules #rule`\n"
            "`!setup show`\n"
            "`!setup setadmin @Role`\n"
            "`!setup addadmin @Role` / `!setup deladmin @Role`\n"
            "`!setup setmod @Role`\n"
            "`!setup addmod @Role` / `!setup delmod @Role`\n"
            "`!setup setwelcome #channel` / `!setup clearwelcome`\n"
            "`!setup setmodlog #channel` / `!setup clearmodlog`\n"
            "`!setup setautorole @Role` / `!setup clearautorole`\n"
        )

    @commands.guild_only()
    @setup_group.command(name="show")
    @admin_or_owner()
    async def show(self, ctx: commands.Context):
        if ctx.guild is None:
            return  # for type-checker safety

        gid = ctx.guild.id

        admin_ids = config.server_config.get_role_ids(gid, config.ADMIN_ROLE_IDS_KEY)
        mod_ids = config.server_config.get_role_ids(gid, config.MOD_ROLE_IDS_KEY)

        welcome_id = config.server_config.get_channel_id(
            gid, config.WELCOME_CHANNEL_ID_KEY
        )
        modlog_id = config.server_config.get_channel_id(
            gid, config.MOD_LOG_CHANNEL_ID_KEY
        )
        rules_id = config.server_config.get_channel_id(gid, config.RULES_CHANNEL_ID_KEY)

        autorole_id = config.server_config.get_id(gid, config.AUTO_ROLE_ID_KEY)

        def role_name(rid: int) -> str:
            r = ctx.guild.get_role(rid)  # type: ignore
            return r.name if r else f"(missing role {rid})"

        def chan_display(cid: int | None) -> str:
            if cid is None:
                return "None"
            c = ctx.guild.get_channel(cid)  # type: ignore
            return (
                c.mention
                if isinstance(c, discord.abc.GuildChannel)
                else f"(missing channel {cid})"
            )

        msg = (
            f"**Server Setup:**\n"
            f"Admin roles: {', '.join(role_name(x) for x in admin_ids) or 'None'}\n"
            f"Mod roles: {', '.join(role_name(x) for x in mod_ids) or 'None'}\n"
            f"Rules channel: {chan_display(rules_id)}\n"
            f"Welcome channel: {chan_display(welcome_id)}\n"
            f"Mod-log channel: {chan_display(modlog_id)}\n"
            f"Auto-role: {role_name(autorole_id) if autorole_id else 'None'}"
        )

        await ctx.send(msg)

    # ----- Admin roles -----
    @setup_group.command(name="setrules")
    @commands.guild_only()
    @mod_or_higher()
    async def setrules(self, ctx: commands.Context, channel: discord.TextChannel):
        config.server_config.set_channel_id(
            ctx.guild.id, config.RULES_CHANNEL_ID_KEY, channel.id  # type: ignore
        )
        await ctx.send(f"✅ Rules channel set to {channel.mention}")

    @commands.guild_only()
    @setup_group.command(name="setadmin")
    @admin_or_owner()
    async def setadmin(self, ctx: commands.Context, role: discord.Role):
        if ctx.guild is None:
            return
        config.server_config.set_role_ids(
            ctx.guild.id, config.ADMIN_ROLE_IDS_KEY, [role.id]
        )
        await ctx.send(f"✅ Admin roles set to: {role.mention}")

    @commands.guild_only()
    @setup_group.command(name="addadmin")
    @admin_or_owner()
    async def addadmin(self, ctx: commands.Context, role: discord.Role):
        if ctx.guild is None:
            return
        gid = ctx.guild.id
        ids = config.server_config.get_role_ids(gid, config.ADMIN_ROLE_IDS_KEY)
        if role.id not in ids:
            ids.append(role.id)
            config.server_config.set_role_ids(gid, config.ADMIN_ROLE_IDS_KEY, ids)
        await ctx.send(f"✅ Added admin role: {role.mention}")

    @commands.guild_only()
    @setup_group.command(name="deladmin")
    @admin_or_owner()
    async def deladmin(self, ctx: commands.Context, role: discord.Role):
        if ctx.guild is None:
            return
        gid = ctx.guild.id
        ids = config.server_config.get_role_ids(gid, config.ADMIN_ROLE_IDS_KEY)
        ids = [x for x in ids if x != role.id]
        config.server_config.set_role_ids(gid, config.ADMIN_ROLE_IDS_KEY, ids)
        await ctx.send(f"✅ Removed admin role: {role.mention}")

    # ----- Mod roles -----
    @commands.guild_only()
    @setup_group.command(name="setmod")
    @admin_or_owner()
    async def setmod(self, ctx: commands.Context, role: discord.Role):
        if ctx.guild is None:
            return
        config.server_config.set_role_ids(
            ctx.guild.id, config.MOD_ROLE_IDS_KEY, [role.id]
        )
        await ctx.send(f"✅ Mod roles set to: {role.mention}")

    @commands.guild_only()
    @setup_group.command(name="addmod")
    @admin_or_owner()
    async def addmod(self, ctx: commands.Context, role: discord.Role):
        if ctx.guild is None:
            return
        gid = ctx.guild.id
        ids = config.server_config.get_role_ids(gid, config.MOD_ROLE_IDS_KEY)
        if role.id not in ids:
            ids.append(role.id)
            config.server_config.set_role_ids(gid, config.MOD_ROLE_IDS_KEY, ids)
        await ctx.send(f"✅ Added mod role: {role.mention}")

    @commands.guild_only()
    @setup_group.command(name="delmod")
    @admin_or_owner()
    async def delmod(self, ctx: commands.Context, role: discord.Role):
        if ctx.guild is None:
            return
        gid = ctx.guild.id
        ids = config.server_config.get_role_ids(gid, config.MOD_ROLE_IDS_KEY)
        ids = [x for x in ids if x != role.id]
        config.server_config.set_role_ids(gid, config.MOD_ROLE_IDS_KEY, ids)
        await ctx.send(f"✅ Removed mod role: {role.mention}")

    # ----- Channels -----
    @commands.guild_only()
    @setup_group.command(name="setwelcome")
    @admin_or_owner()
    async def setwelcome(self, ctx: commands.Context, channel: discord.TextChannel):
        if ctx.guild is None:
            return
        config.server_config.set_channel_id(
            ctx.guild.id, config.WELCOME_CHANNEL_ID_KEY, channel.id
        )
        await ctx.send(f"✅ Welcome channel set to: {channel.mention}")

    @commands.guild_only()
    @setup_group.command(name="clearwelcome")
    @admin_or_owner()
    async def clearwelcome(self, ctx: commands.Context):
        if ctx.guild is None:
            return
        config.server_config.set_channel_id(
            ctx.guild.id, config.WELCOME_CHANNEL_ID_KEY, None
        )
        await ctx.send("✅ Welcome channel cleared.")

    @commands.guild_only()
    @setup_group.command(name="setmodlog")
    @admin_or_owner()
    async def setmodlog(self, ctx: commands.Context, channel: discord.TextChannel):
        if ctx.guild is None:
            return
        config.server_config.set_channel_id(
            ctx.guild.id, config.MOD_LOG_CHANNEL_ID_KEY, channel.id
        )
        await ctx.send(f"✅ Mod-log channel set to: {channel.mention}")

    @commands.guild_only()
    @setup_group.command(name="clearmodlog")
    @admin_or_owner()
    async def clearmodlog(self, ctx: commands.Context):
        if ctx.guild is None:
            return
        config.server_config.set_channel_id(
            ctx.guild.id, config.MOD_LOG_CHANNEL_ID_KEY, None
        )
        await ctx.send("✅ Mod-log channel cleared.")

    # ----- Auto-role -----
    @commands.guild_only()
    @setup_group.command(name="setautorole")
    @admin_or_owner()
    async def setautorole(self, ctx: commands.Context, role: discord.Role):
        if ctx.guild is None:
            return
        config.server_config.set_id(ctx.guild.id, config.AUTO_ROLE_ID_KEY, role.id)
        await ctx.send(f"✅ Auto-role set to: {role.mention}")

    @commands.guild_only()
    @setup_group.command(name="clearautorole")
    @admin_or_owner()
    async def clearautorole(self, ctx: commands.Context):
        if ctx.guild is None:
            return
        config.server_config.set_id(ctx.guild.id, config.AUTO_ROLE_ID_KEY, None)
        await ctx.send("✅ Auto-role cleared.")


async def setup(bot: commands.Bot):
    await bot.add_cog(Setup(bot))
