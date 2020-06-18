import discord
from discord.ext import commands
from re import match
import asyncio
from bot.constants import highest_admin_role_id, mute_role_id, admin_roles
from bot.Cogs.Moderation import time as t


class AdminUtils(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.has_any_role(*admin_roles)
    async def mute(self, ctx, *args):
        user_ids = []
        times = []
        for i in range(len(args)):
            arg = args[i].strip('.,:\'<>[]{}()')
            if match(r'\d+[smhd]{1}', arg):
                times.append(arg)

            elif match(r'\d+', arg):
                user_ids.append(int(arg))

            else:
                #reason = ' '.join(args[i: ])
                break
        duration = t.get_total_time(times)

        print(user_ids)
        users = []
        user_names = []
        for user_id in user_ids:
            user = ctx.guild.get_member(user_id)
            print(user)
            users.append(user)
            user_names.append(user.display_name)
        user_names = ', '.join(user_names)

        self.mute_role = ctx.guild.get_role(mute_role_id)
        for user in users:
            await user.add_roles(self.mute_role)
        if duration:
            await asyncio.sleep(duration)
            for user in users:
                await user.remove_roles(self.mute_role)

    @commands.command()
    @commands.has_any_role(*admin_roles)
    async def unmute(self, ctx, *user_ids):
        for user_id in user_ids:
            user = ctx.guild.get_member(int(user_id))
            if user.top_role.id == mute_role_id:
                await user.remove_roles(self.mute_role)
            else:
                await ctx.send(f'{user.display_name} is not muted')

def setup(client):
    client.add_cog(AdminUtils(client))
