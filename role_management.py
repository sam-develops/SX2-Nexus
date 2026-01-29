import discord
from discord.ext import commands

class RoleManagement(commands.Cog):
    """Admin commands to manage server roles."""
    category = "Admin"

    def __init__(self, bot):
        self.bot = bot

    # -------------------------
    # Add role to a member
    # -------------------------
    @commands.command(name="addrole", help="Assign a role to a user.")
    @commands.has_permissions(administrator=True)
    async def add_role(self, ctx, member: discord.Member, role: discord.Role):
        if role in member.roles:
            await ctx.send(f"⚠️ {member.mention} already has {role.mention}")
            return
        try:
            await member.add_roles(role, reason=f"Added by {ctx.author}")
            await ctx.send(f"✅ Added {role.mention} to {member.mention}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to add that role.")
        except Exception as e:
            await ctx.send(f"❌ Unexpected error: {e}")

    # -------------------------
    # Remove role from a member
    # -------------------------
    @commands.command(name="removerole", help="Remove a role from a user.")
    @commands.has_permissions(administrator=True)
    async def remove_role(self, ctx, member: discord.Member, role: discord.Role):
        if role not in member.roles:
            await ctx.send(f"⚠️ {member.mention} does not have {role.mention}")
            return
        try:
            await member.remove_roles(role, reason=f"Removed by {ctx.author}")
            await ctx.send(f"✅ Removed {role.mention} from {member.mention}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to remove that role.")
        except Exception as e:
            await ctx.send(f"❌ Unexpected error: {e}")

    # -------------------------
    # Create a role
    # -------------------------
    @commands.command(name="createrole", help="Create a new role. Optional hex color: #FF0000")
    @commands.has_permissions(administrator=True)
    async def create_role(self, ctx, name: str, color: str = None): # type: ignore
        try:
            role_color = discord.Color.default()
            if color:
                if color.startswith("#"):
                    color = color.lstrip("#")
                try:
                    role_color = discord.Color(int(color, 16))
                except ValueError:
                    await ctx.send("❌ Invalid color hex. Using default color.")
            new_role = await ctx.guild.create_role(name=name, color=role_color, reason=f"Created by {ctx.author}")
            await ctx.send(f"✅ Role created: {new_role.mention}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to create roles.")
        except Exception as e:
            await ctx.send(f"❌ Unexpected error: {e}")

    # -------------------------
    # Delete a role
    # -------------------------
    @commands.command(name="deleterole", help="Delete a role from the server.")
    @commands.has_permissions(administrator=True)
    async def delete_role(self, ctx, role: discord.Role):
        try:
            await role.delete(reason=f"Deleted by {ctx.author}")
            await ctx.send(f"✅ Deleted role: {role.name}")
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to delete that role.")
        except Exception as e:
            await ctx.send(f"❌ Unexpected error: {e}")

    # -------------------------
    # List roles
    # -------------------------
    @commands.command(name="listroles", help="List roles for a user or all server roles.")
    @commands.has_permissions(administrator=True)
    async def list_roles(self, ctx, member: discord.Member = None): # type: ignore
        if member:
            roles = [r.mention for r in member.roles if r != ctx.guild.default_role]
            roles_str = ", ".join(roles) if roles else "None"
            await ctx.send(f"👤 Roles for {member.mention}: {roles_str}")
        else:
            roles = [r.mention for r in ctx.guild.roles if r != ctx.guild.default_role]
            roles_str = ", ".join(roles) if roles else "None"
            await ctx.send(f"📋 Server Roles: {roles_str}")

async def setup(bot):
    await bot.add_cog(RoleManagement(bot))
