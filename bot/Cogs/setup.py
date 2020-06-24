import sqlite3
import discord
from discord.ext import commands
import discord.utils as utils
from bot.Cogs.Moderation import infractions
from datetime import datetime
from re import findall
from bot.Cogs.utils import db_funcs
import json
from os import getcwd


def is_admin(): 
    async def predicate(ctx):
        admin_role_ids = db_funcs.get_from_guild(ctx.guild.id, 'admin_role_ids').split(' ')
        admin_roles = []
        # guild_roles = await ctx.guild.fetch_roles()
        # print(guild_roles)
        # print([role.id for role in guild_roles])
        for role_id in admin_role_ids:
            # admin_roles.append(utils.get(guild_roles, id=role_id))
            admin_roles.append(ctx.guild.get_role(role_id))

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

    @commands.command(aliases=['mrole', 'muterole'])
    @is_admin()
    async def mute_role(self, ctx, m_role_id=None):
        if '-r' in ctx.message.content:
            db_funcs.update_guild(ctx.guild.id, 'mute_role_id', '0')
            await ctx.send('Resetting the mute role')
            return

        try:
            if not m_role_id:
                m_role_id = 0
            else:
                m_role_id = int(m_role_id)
        except ValueError:
            await ctx.send('That is not a valid role id!')
            return
            
        if m_role_id:
            db_funcs.update_guild(ctx.guild.id, 'mute_role_id', m_role_id)

        else:
            curr_vm_role = db_funcs.get_from_guild(ctx.guild.id, 'mute_role_id')
            await ctx.send(f'The current mute role is: `{ctx.guild.get_role(curr_vm_role).name}`')

    @commands.command(aliases=['vmrole', 'voicemuterole'])
    @is_admin()
    async def voice_mute_role(self, ctx, vm_role_id=None):
        if '-r' in ctx.message.content:
            db_funcs.update_guild(ctx.guild.id, 'voice_mute_role_id', '0')
            await ctx.send('Resetting the voice mute role')
            return

        try:
            if not vm_role_id:
                vm_role_id = 0
            else:
                vm_role_id = int(vm_role_id)
        except ValueError:
            await ctx.send('That is not a valid role id!')
            return

        if vm_role_id:
            db_funcs.update_guild(ctx.guild.id, 'voice_mute_role_id', vm_role_id)

        else:
            curr_vm_role = db_funcs.get_from_guild(ctx.guild.id, 'voice_mute_role_id')
            await ctx.send(f'The current voice channel mute role is: `{str(ctx.guild.get_role(curr_vm_role))}`')

    @commands.command(aliases=['adminroles', 'admins'])
    @is_admin()
    async def admin_roles(self, ctx):
        new_admin_role_ids = " ".join(findall(r'\d{18}', ctx.message.content))
        if '-r' in ctx.message.content:
            db_funcs.update_guild(ctx.guild.id, 'admin_role_ids', '0')
            await ctx.send('Resetting admin roles')
            return

        if new_admin_role_ids:
            curr_admin_role_ids = db_funcs.get_from_guild(ctx.guild.id, 'admin_role_ids')
            if curr_admin_role_ids != '0':
                new_admin_role_ids = f'{curr_admin_role_ids} {new_admin_role_ids}'

            db_funcs.update_guild(ctx.guild.id, 'admin_role_ids', new_admin_role_ids)

        else:
            curr_admin_role_ids = db_funcs.get_from_guild(ctx.guild.id, 'admin_role_ids').split(' ')
            role_names = []
            for role_id in curr_admin_role_ids:
                role = ctx.guild.get_role(int(role_id))
                role_names.append(f'`{str(role)}`')

            admin_roles = ", ".join(role_names)
            await ctx.send(f'The current roles with elevated permissions are: {admin_roles}')

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
        db_funcs.update_guild(ctx.guild.id, 'prefix', new_prefix)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        '''Adds a row to the server_specific table for the guild on joining a server'''
        db_funcs.guild_init(guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        '''Remove the guild and it's prefix from the db because space'''
        self.c.execute("""DELETE FROM server_specific WHERE guild_id=:id""",
                        {
                            'id': guild.id
                        })
        self.conn.commit()
        with open(f'{getcwd()}\\bot\\guild_log.json', 'r') as guild_log:
            guilds_inits = json.load(guild_log)
            guilds_inits.remove(guild.id)
            guild_log.write(json.dumps(guilds_inits))

    @commands.Cog.listener()
    async def on_ready(self):
        '''If the bot joins a server but is offline, it will not initialise the data in the db, so it keeps a log of the guilds it's in and inits ones it's not in'''
        with open(f'{getcwd()}/guild_log.json', 'r') as f:
            guilds_inited = set(json.load(f))
            for bot_guild in self.client.guilds:
                if bot_guild.id not in guilds_inited:
                    db_funcs.guild_init(bot_guild.id)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        '''Sends 'command not found' if a wrong command is entered'''
        if isinstance(error, commands.CommandNotFound):
            command = ctx.message.content.split(' ')[0]
            await ctx.send(f'Command `{command}` not found')


def setup(client):
    client.add_cog(Setup(client))
