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
        self.conn = sqlite3.connect('discord_bot.db')
        self.c = self.conn.cursor()

    def disable_infraction(self, infraction_id):
        self.c.execute("""UPDATE infractions
                            SET active=0
                            WHERE id=:id""",
                            {
                                'id': infraction_id
                            })
        self.conn.commit()

    def add_infraction(self, _id, guild_id, user_id, admin_id, _type, duration, reason):
        '''Adds an infraction to the database and applies it to the user, the task disable_expired_infractions handles the timing for disabling'''
        self.c.execute("""INSERT INTO infractions(id, active , guild_id, user_id, admin, type, expires, reason)
                            VALUES (:id, :active, :g_id, :u_id, :admin_id, :type, :expires, :reason)""",
                            {
                                'id': _id,
                                'active': 1,
                                'g_id': guild_id,
                                'u_id': user_id,
                                'admin_id': admin_id,
                                'type': _type,
                                'expires': datetime.utcnow() + timedelta(seconds=duration),
                                'reason': reason
                            }
                        )
        self.conn.commit()

    @commands.command(category='moderation', cls=utils.Command)
    @utils.is_admin()
    async def mute(self, ctx):
        '''Mutes all the users from the list of IDs provided
        Usage:
        `{prefix}mute 258306791174176770 474515215128461324`'''
        mute_role_id = db_funcs.get_from_guild(ctx.guild.id, 'mute_role_id')
        if not mute_role_id:
            await ctx.send('Mute role not set for the sever, not executing command')
            return
        mute_role = ctx.guild.get_role(mute_role_id)

        user_ids = findall(r'\d{18}', ctx.message.content)
        duration = utils.get_total_time(ctx.message.content)
        try:
            reason = findall(r'".+"', ctx.message.content)[0]
        except IndexError:
            empty_reason_question = await ctx.send('No string inside quotes found, do you want to apply an infraction without a reason?')
            admin_id = ctx.message.author.id
            await empty_reason_question.add_reaction('✔')
            try:
                def check(reaction, user):
                    return str(reaction) == '✔' and user.id == admin_id and reaction.message.id == empty_reason_question.id
                await self.client.wait_for('reaction_add', check=check, timeout=60)
                await empty_reason_question.clear_reactions()
                reason = 'No reason given'
            except asyncio.TimeoutError:
                await ctx.send('Not adding infraction without confirmation for empty reason')
                return

        feedback_msg = f'Users {", ".join(user_ids)} muted for {duration} seconds.'
        if reason != 'No reason given':
            feedback_msg += f' Reason: {reason}'
        await ctx.send(feedback_msg)

        for user_id in user_ids:
            user = ctx.guild.get_member(int(user_id))
            await user.add_roles(mute_role)
            self.add_infraction(ctx.message.id, ctx.guild.id, user_id, ctx.message.author.id, 'mute', duration, reason)

    @commands.command(category='moderation', cls=utils.Command)
    @utils.is_admin()
    async def unmute(self, ctx=None, guild=None, user=None):
        '''Unmutes all of the users from the list of  IDs provided
        Usage:
        `{prefix}unmute 258306791174176770 474515215128461324`'''
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
            await self.add_infraction(ctx.message.id, g_id, u_id, self.client.id, 'mute', duration, reason)

    @tasks.loop(seconds=5.0)
    async def disable_expired_infractions(self):
        '''Checks if any infractions have expired every 5 seconds because I don't want to break my PC by running asyncio.sleep 500 times'''
        expired_infractions = db_funcs.get_expired_infractions()
        print(expired_infractions)

        if expired_infractions:
            for infraction in expired_infractions:
                guild = await self.client.fetch_guild(infraction['guild_id'])
                user = guild.get_member(infraction['user_id'])
                _type = infraction['type']
                await self.unmute(guild=guild, user=user)

                infraction_id = infraction['id']
                self.disable_infraction(infraction_id)

    @commands.Cog.listener()
    async def on_ready(self):
        self.disable_expired_infractions.start() # pylint: disable=maybe-no-member


def setup(client):
    client.add_cog(Infractions(client))
