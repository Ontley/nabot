import discord
from discord.ext import commands
from re import match
import asyncio
from bot.constants import mute_role_id, admin_roles
from bot.Cogs.utils import time


class Infractions(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def apply_mute(self, ctx, user_ids, duration):
        mute_role = ctx.guild.get_role(mute_role_id)
        for user_id in user_ids:
            user = ctx.guild.get_member(user_id)
            await user.add_roles(mute_role)

        if duration:
            await asyncio.sleep(duration)
            for user_id in user_ids:
                user = ctx.guild.get_member(user_id)
                await user.remove_roles(mute_role)

    @commands.command()
    @commands.has_any_role(*admin_roles)
    async def mute(self, ctx, *args):
        '''Mutes the users from the IDs provided'''
        user_ids = []
        times = []

        '''Getting needed elements from the args'''
        for i in range(len(args)):
            arg = args[i].strip('.,:\'\\<>[]{\}()')
            if match(r'\d+[smhd]{1}', arg):
                times.append(arg)

            elif match(r'\d+', arg):
                user_ids.append(int(arg))

            else:
                #reason = ' '.join(args[i: ])
                break
        duration = time.get_total_time(times)
        await self.apply_mute(ctx, user_ids, duration)
        

    @commands.command()
    @commands.has_any_role(*admin_roles)
    async def unmute(self, ctx, *user_ids):
        '''Unmutes all of the users from the IDs provided'''
        mute_role = ctx.guild.get_role(mute_role_id)
        for user_id in user_ids:
            user = ctx.guild.get_member(int(user_id))
            if user.top_role.id == mute_role_id:
                await user.remove_roles(mute_role)
            else:
                await ctx.send(f'{user.display_name} is not muted')

    @commands.Cog.listener()
    async def on_member_join(self, ctx):
        '''This reapplies mutes and other active infractions the user had if they left'''
        # database stuff

        # reapply the infractions

        pass # remove

def setup(client):
    client.add_cog(Infractions(client))
