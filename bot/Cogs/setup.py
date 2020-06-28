import sqlite3
import discord
from discord.ext import commands
import discord.utils as utils
from bot.Cogs.Moderation import infractions
from datetime import datetime
from re import findall
from bot.Cogs.utils import db_funcs, utils
from bot.Cogs.utils.utils import Command
import json
from os import getcwd


class Setup(commands.Cog):
    '''Server setup commands'''
    def __init__(self, client):
        self.client = client
        self.conn = sqlite3.connect('discord_bot.db')
        self.conn.row_factory = sqlite3.Row
        self.c = self.conn.cursor()

    @commands.command(aliases=['mrole', 'mute_role'], category='setup', cls=Command)
    @utils.is_admin()
    async def muterole(self, ctx, m_role_id=None):
        '''Allows moderators to assign which role a user is given when given the mute infraction, or view the current one
        Usage:
        `{prefix}muterole 725311689418997771`
        `{prefix}muterole` '''
        if '-r' in ctx.message.content:
            db_funcs.update_in_guild(ctx.guild.id, 'mute_role_id', '0')
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
            db_funcs.update_in_guild(ctx.guild.id, 'mute_role_id', m_role_id)
            await ctx.send(f'Set role id {m_role_id} as mute role')

        else:
            curr_m_role = db_funcs.get_from_guild(ctx.guild.id, 'mute_role_id')
            if curr_m_role == 0:
                await ctx.send('No mute role set, timeout mechanic and mute infraction are disabled')
                return
            role_name = str(ctx.guild.get_role(curr_m_role))
            await ctx.send(f'The current mute role is: `{role_name}`')

    @commands.command(category='setup', cls=Command)
    @utils.is_admin()
    async def admins(self, ctx):
        '''Allows the owner to edit which roles have access to moderation commands, or view current ones
        Usage:
        `{prefix}admins 724609221148147834 725313041889230868`
        `{prefix}` '''
        new_admin_role_ids = " ".join(findall(r'\d{18}', ctx.message.content))
        if '-r' in ctx.message.content:
            db_funcs.update_in_guild(ctx.guild.id, 'admin_role_ids', '0')
            await ctx.send('Resetting admin roles')
            return

        if new_admin_role_ids:
            curr_admin_role_ids = db_funcs.get_from_guild(ctx.guild.id, 'admin_role_ids')
            if curr_admin_role_ids != '0':
                new_admin_role_ids = f'{curr_admin_role_ids} {new_admin_role_ids}'

            db_funcs.update_in_guild(ctx.guild.id, 'admin_role_ids', new_admin_role_ids)

        else:
            curr_admin_role_ids = db_funcs.get_from_guild(ctx.guild.id, 'admin_role_ids').split(' ')
            role_names = []
            for role_id in curr_admin_role_ids:
                role = ctx.guild.get_role(int(role_id))
                if role:
                    role_names.append(f'`{str(role)}`')

            if role_names:
                admin_roles = ", ".join(role_names)
                await ctx.send(f'The current roles with elevated permissions are: {admin_roles}')
                return
            await ctx.send('No moderator roles set, only server owner can execute moderator commands')

    @commands.command(category='setup', cls=Command)
    async def prefix(self, ctx, new_prefix=None):
        '''Allows server owner to change my prefix for this server or view the current one
        Usage:
        `{prefix}prefix !!`
        {prefix}prefix` '''
        if new_prefix:
            if ctx.author == ctx.guild.owner:
                db_funcs.update_in_guild(ctx.guild.id, 'prefix', new_prefix)
                await ctx.send(f'The new server prefix is: {new_prefix}')
                
            else:
                await ctx.send('You don\'t have the required permissions to change the server command prefix')

        else:
            curr_prefix = db_funcs.get_from_guild(ctx.guild.id, 'prefix')
            await ctx.send(f'The server\'s current prefix is {curr_prefix}')

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
        with open(f'{getcwd()}\\bot\\guild_log.json', 'r+') as guild_log:
            guilds_inits = json.load(guild_log)
            guilds_inits.remove(guild.id)
            guild_log.seek(0)
            guild_log.write(json.dumps(guilds_inits))
            guild_log.truncate()

    @commands.Cog.listener()
    async def on_ready(self):
        '''If the bot joins a server but is offline, it will not initialise the data in the db, so it keeps a log of the guilds it's in and inits ones it's not in'''
        with open(f'{getcwd()}\\bot\\guild_log.json', 'r') as f:
            guilds_inited = set(json.load(f))
            for bot_guild in self.client.guilds:
                if bot_guild.id not in guilds_inited:
                    db_funcs.guild_init(bot_guild.id)


def setup(client):
    client.add_cog(Setup(client))
