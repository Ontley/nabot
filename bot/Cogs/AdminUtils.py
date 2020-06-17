import discord
from discord.ext import commands
from re import match
import asyncio
from bot.constants import highest_admin_role_id, mute_role_id, admin_roles


def get_total_time(times):
    total = 0
    for time in times:
        try:
            total += int(time)
        except ValueError:
            try:
                time_value = int(time[:-1])
                time_multi = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}[time[-1]]
                total += time_value * time_multi
            except KeyError:
                print('Mute dicitonary key error, skipping current time request')
    return total


async def shorten_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    time_str = ''
    if days:
        time_str += f'{days} days '
    if hours:
        time_str += f'{hours} hours '
    if minutes:
        time_str += f'{minutes} minutes '
    if seconds:
        time_str += f'{seconds} seconds '
    return time_str


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
        duration = get_total_time(times)

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
            user = ctx.guild.get_role(user_id)
            if user.top_role.id == mute_role_id:
                await user.remove_roles(self.mute_role)
            else:
                await ctx.send(f'{user.display_name} is not muted')

def setup(client):
    client.add_cog(AdminUtils(client))
