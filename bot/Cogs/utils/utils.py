import datetime
from re import findall
from discord.ext import commands
import db_funcs

def get_total_time(string):
    '''Returns total seconds specified in string i.e. '1h 30m' is 5400 seconds'''
    times = findall(r'\d+[smhd]{1}', string)
    total = 0
    for time in times:
        try:
            time_value = map(list, findall(r'\d+', time))
            multi = findall(r'[smhd]{1}', time)
            multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
            time_multi = multipliers[multi]
            total += time_value * time_multi
        except KeyError:
            print('Mute dictionary key error, skipping current time request')
    return total


def shorten_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    time_str = ''
    if days > 1:
        time_str += f'{days} days '
    elif days == 1:
        time_str += f'{days} day '
    if hours > 1:
        time_str += f'{hours} hours '
    elif hours == 1:
        time_str += f'{hours} hour '
    if minutes > 1:
        time_str += f'{minutes} minutes '
    elif minutes == 1:
        time_str += f'{minutes} minute '
    if seconds > 1:
        time_str += f'{seconds} seconds '
    elif seconds == 1:
        time_str += f'{seconds} second '
    return time_str

def is_admin(): 
    async def predicate(ctx):
        admin_role_ids = db_funcs.get_from_guild(ctx.guild.id, 'admin_role_ids').split(' ')
        admin_roles = []
        for role_id in admin_role_ids:
            admin_roles.append(ctx.guild.get_role(role_id))

        user_roles = ctx.author.roles
        if any(u_role in admin_roles for u_role in user_roles):
            return True
        elif ctx.author == ctx.guild.owner or ctx.author.id == 258306791174176770: # dunno if I should keep the id bypass
            return True

        await ctx.send('You don\'t have the required role to do this!')
        return False

    return commands.check(predicate)