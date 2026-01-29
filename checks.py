from discord.ext import commands
import config


def _has_any_role_id(member, role_ids: list[int]) -> bool:
    member_role_ids = {r.id for r in getattr(member, "roles", [])}
    return any(rid in member_role_ids for rid in role_ids)


def admin_or_owner():
    async def predicate(ctx):
        if not ctx.guild:
            return False
        if ctx.author.id == ctx.guild.owner_id:
            return True

        admin_ids = config.server_config.get_role_ids(
            ctx.guild.id, config.ADMIN_ROLE_IDS_KEY
        )
        return _has_any_role_id(ctx.author, admin_ids)

    return commands.check(predicate)


def mod_or_higher():
    async def predicate(ctx):
        if not ctx.guild:
            return False
        if ctx.author.id == ctx.guild.owner_id:
            return True

        admin_ids = config.server_config.get_role_ids(
            ctx.guild.id, config.ADMIN_ROLE_IDS_KEY
        )
        mod_ids = config.server_config.get_role_ids(
            ctx.guild.id, config.MOD_ROLE_IDS_KEY
        )

        if _has_any_role_id(ctx.author, admin_ids):
            return True
        return _has_any_role_id(ctx.author, mod_ids)

    return commands.check(predicate)
