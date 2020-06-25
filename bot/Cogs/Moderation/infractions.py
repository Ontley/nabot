import sqlite3
import discord
from discord.ext import commands, tasks
from re import findall
import asyncio
from bot.Cogs.utils import db_funcs, utils
from datetime import timedelta, datetime


class Infractions(commands.Cog):
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def add_infraction(_id, guild, user, _type, duration, reason):
        '''Adds an infraction to the database and applies it to the user, the task disable_expired_infractions handles the timing for disabling'''
        conn = sqlite3.connect('discord_bot.db')
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
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
        conn.commit()

    @commands.command()
    @utils.is_admin()
    async def mute(self, ctx):
        '''Mutes the users from the IDs provided'''
        mute_role_id = db_funcs.get_from_guild(ctx.guild.id, 'mute_role_id')
        mute_role = ctx.guild.get_role(int(mute_role_id))

        user_ids = findall(r'\d{18}', ctx.message.content)
        duration = utils.get_total_time(ctx.message.content)
        reason = findall(r'".+"', ctx.message.content)
        for user_id in user_ids:
            user = ctx.guild.get_member(user_id)
            await user.add_roles(mute_role)
            await self.add_infraction(ctx.message.id, ctx.guild, user_id, 'mute', duration, reason)

    @commands.command()
    @utils.is_admin()
    async def unmute(self, ctx=None, guild=None, user=None):
        '''Unmutes all of the users from the IDs provided'''
        print('got into unmute')
        # mute_role_id = db_funcs.get_from_guild(ctx.guild.id, 'mute_role_id')
        # mute_role = ctx.guild.get_role(int(mute_role_id))
        
        # user_ids = findall(r'\d{18}', ctx.message.content)
        # for user_id in user_ids:
        #     user = ctx.guild.get_member(int(user_id))
        #     await user.remove_roles(mute_role)
        
    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        '''This reapplies mutes the user had if they left and rejoined'''
        active_mute = db_funcs.grab_user_infractions(ctx.author.id)
        if active_mute:
            g_id = ctx.guild.id
            u_id = ctx.author.id
            duration = active_mute['duration']
            reason = f'REAPPLIED ON REJOIN: \'{active_mute["reason"]}\''
            await self.add_infraction(ctx.message.id, g_id, u_id, 'mute', duration, reason)

    @tasks.loop(seconds=5.0)
    async def disable_expired_infractions(self):
        '''Checks if any infractions have expired every 5 seconds because I don't want to break my PC by running asyncio.sleep 500 times'''
        expired_infractions = db_funcs.get_expired_infractions()

        if expired_infractions:
            for infraction in expired_infractions:
                guild = self.client.get_guild(infraction['guild_id'])
                user = guild.get_member(infraction['user_id'])
                _type = infraction['type']
                await self.unmute(guild=guild, user=user)
                
                # await disable_infraction(guild, user, _type)
                # disable the infractions found


def setup(client):
    client.add_cog(Infractions(client))
