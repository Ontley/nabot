import sqlite3
import discord
from discord.ext import commands
from bot.Cogs.Moderation import infractions
from datetime import datetime
from re import findall
from bot.Cogs.utils import db_funcs


def is_admin(): 
    async def predicate(ctx):
        admin_role_ids = db_funcs.get_from_guild(ctx.guild.id, 'admin_role_ids')
        admin_roles = []
        for _id in admin_role_ids:
            admin_roles.append(ctx.guild.get_role(int(_id)))

        user_roles = ctx.author.roles
        if any(u_role in admin_roles for u_role in user_roles):
            return True
        elif ctx.author == ctx.guild.owner or ctx.author.id == 258306791174176770:
            return True

        await ctx.send('You don\'t have the required role to do this!')
        return False

    return commands.check(predicate)


class Setup(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.conn = sqlite3.connect('discord_bot.db')
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        '''Sends command not found if a wrong command is entered'''
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f'Command {ctx.command.name} not found')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        '''Give the guild the default ++ prefix for commands'''
        self.c.execute("""INSERT INTO server_specific(guild_id, prefix, mute_role_id, voice_mute_role_id, admin_role_ids) 
                        VALUES (:g_id, :prefix, :m_role, :vm_role, :a_roles)""", 
                        {
                            'g_id': guild.id,
                            'prefix': '++',
                            'm_role': 0,
                            'vm_role': 0,
                            'a_roles': '0'
                        })
        self.conn.commit()


    @commands.command(aliases=['mrole', 'muterole'])
    @is_admin()
    async def mute_role(self, ctx, m_role_id=None):
        try:
            m_role_id = int(m_role_id)
        except ValueError:
            ctx.send('That is not a valid role id!')
            return
            
        if m_role_id:
            self.c.execute("""UPDATE server_specific SET mute_role_id=:m_role WHERE guild_id=:g_id""",
                            {
                                'm_role': m_role_id
                            })
            self.conn.commit()

        else:
            curr_vm_role = db_funcs.get_from_guild(ctx.guild.id, 'mute_role_id')
            ctx.send(f'The current mute role is {ctx.guild.get_role(curr_vm_role).name}')

    @commands.command(aliases=['vmrole', 'voicemuterole'])
    @is_admin()
    async def voice_mute_role(self, ctx, vm_role_id=None):
        try:
            vm_role_id = int(vm_role_id)
        except ValueError:
            ctx.send('That is not a valid role id!')
            return

        if vm_role_id:
            self.c.execute("""UPDATE server_specific SET voice_mute_role_id=:vm_role WHERE guild_id=:g_id""",
                            {
                                'vm_role': vm_role_id
                            })
            self.conn.commit()

        else:
            curr_vm_role = db_funcs.get_from_guild(ctx.guild.id, 'voice_mute_role_id')
            ctx.send(f'The current voice channel mute role is {ctx.guild.get_role(curr_vm_role).name}')

    @commands.command(aliases=['adminroles'])
    @is_admin()
    async def admin_roles(self, ctx):
        new_admin_role_ids = " ".join(findall(r'\d{18}', ctx.message.content))
        if new_admin_role_ids:
            if '-r' not in ctx.message.content:
                curr_admin_role_ids = db_funcs.get_from_guild(ctx.guild.id, 'admin_roles')
                new_admin_role_ids += curr_admin_role_ids

            self.c.execute("""UPDATE server_specific SET admin_role_ids=:a_roles WHERE guild_id=:g_id""",
                            {
                                'a_roles': new_admin_role_ids,
                                'g_id': ctx.guild.id
                            })
            self.conn.commit()

        else:
            curr_admin_roles = db_funcs.get_from_guild(ctx.guild.id, 'admin_role_ids')
            admin_role_names = ', '.join([ctx.guild.get_role(int(role_id)).name for role_id in curr_admin_roles])
            ctx.send(f'The current \'admin\' roles is {admin_role_names}')

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        '''Remove the guild and it's prefix from the db because space'''
        self.c.execute("""DELETE FROM server_specific WHERE guild_id=:id""",
                        {
                            'id': guild.id
                        })
        self.conn.commit()

    @commands.command()
    async def prefix(self, ctx):
        curr_prefix = db_funcs.get_from_guild(ctx.guild.id, 'prefix')
        await ctx.send(f'The server\'s current prefix is {curr_prefix}')

    @commands.command(aliases=['changeprefix'])
    @is_admin()
    async def change_prefix(self, ctx, new_prefix):
        if not new_prefix:
            await ctx.send('Please provide a new prefix or use the prefix command to view the current one')
            return
        self.c.execute("""UPDATE server_specific SET prefix=:new_prefix WHERE guild_id=:guild_id""",
                        {
                            'guild_id': ctx.guild.id,
                            'new_prefix': new_prefix
                        })
        self.conn.commit()


def setup(client):
    client.add_cog(Setup(client))
