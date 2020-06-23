import sqlite3
import discord
from discord.ext import commands, tasks
from re import match
import asyncio
# from bot.constants import mute_role_id, admin_roles
from bot.Cogs.utils import time
from bot.Cogs.utils import db_funcs
from datetime import timedelta, datetime


conn = sqlite3.connect('discord_bot')
conn.row_factory = sqlite3.Row
c = conn.cursor()


async def disable_infraction(guild, user, _type):
    if _type == 'mute':
        pass
        # mute_role = guild.get_role(mute_role_id)
        # await user.add_roles(mute_role)

    elif _type == 'voicemute':
        pass

    elif _type == 'softban':
        pass


async def apply_infraction(guild, user, _type):
    if _type == 'mute':
        # mute_role = guild.get_role(mute_role_id)
        # await user.add_roles(mute_role)
        pass

    elif _type == 'voicemute':
        pass

    elif _type == 'softban':
        pass


async def add_infraction(_id, guild, user, _type, duration, reason):
    '''Adds an infraction to the database and applies it to the user'''
    c.execute("INSERT INTO infractions VALUES (:id, :active, :g_id, :u_id, :type, :expires, :reason)",
                {
                    'id': _id,
                    'active': 1,
                    'g_id': guild.id,
                    'u_id': user.id,
                    'type': _type,
                    'expires': datetime.utcnow() + timedelta(seconds=duration),
                    'reason': reason
                }
            )
    await apply_infraction(guild, user, _type)


class Infractions(commands.Cog):
    def __init__(self, client):
        self.client = client
        conn = sqlite3.connect('discord_bot.db')
        conn.row_factory = sqlite3.Row
        self.c = conn.cursor()

    @commands.command()
    # @commands.has_any_role(*admin_roles)
    async def mute(self, ctx, *args):
        '''Mutes the users from the IDs provided'''
        user_ids = []
        duration = time.get_total_time(ctx.message.content)

        '''Getting needed elements from the args'''
        for i in range(len(args)):
            if match(r'\d+', args[i]):
                user_ids.append(int(args[i]))

            else:
                reason = ' '.join(args[i: ])
                break
        await add_infraction(ctx.message.id, ctx.guild, user_ids, 'mute', duration, reason)

    @commands.command()
    #@commands.has_any_role(*admin_roles)
    async def unmute(self, ctx, *user_ids):
        '''Unmutes all of the users from the IDs provided'''
        # mute_role = ctx.guild.get_role(mute_role_id)
        # for user_id in user_ids:
        #     user = ctx.guild.get_member(int(user_id))
        #     if user.top_role.id == mute_role_id:
        #         await user.remove_roles(mute_role)
        #     else:
        #         await ctx.send(f'{user.display_name} is not muted')

    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        '''This reapplies mutes the user had if they left and rejoined'''
        active_mute = db_funcs.grab_user_infractions(ctx.author.id)
        if active_mute:
            g_id = ctx.guild.id
            u_id = ctx.author.id
            duration = active_mute['duration']
            reason = f'REAPPLIED ON REJOIN: \'{active_mute["reason"]}\''
            await add_infraction(ctx.message.id, g_id, u_id, 'mute', duration, reason)

    @commands.Cog.listener()
    async def on_ready(self):
        '''if the bot restarts, running infraction timers are lost so tempmutes and tempbans would break.
        This reapplies all active infractions for servers the bot is in'''
        active_infractions = db_funcs.get_active_infractions()

        if active_infractions:
            for infraction in active_infractions:
                guild = self.client.get_guild(infraction['guild_id'])
                user = guild.get_member(infraction['user_id'])
                _type = infraction['type']
                
                await apply_infraction(guild, user, _type)

    @tasks.loop(seconds=10.0)
    async def disable_expired_infractions(self):
        '''Checks if any infractions have expired every 5 seconds because I don't want to break my PC br running 500 coros'''
        expired_infractions = db_funcs.get_expired_infractions()

        if expired_infractions:
            for infraction in expired_infractions:
                guild = self.client.get_guild(infraction['guild_id'])
                user = guild.get_member(infraction['user_id'])
                _type = infraction['type']
                
                await disable_infraction(guild, user, _type)


def setup(client):
    client.add_cog(Infractions(client))
