import datetime
from re import findall
from discord.ext import commands
from bot.Cogs.utils import db_funcs
from datetime import datetime
from enum import Enum


def get_total_time(string):
    '''Returns total seconds specified in string i.e. '1h 30m' is 5400 seconds'''
    multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    times = findall(r'\d+[smhd]{1}', string)

    total = 0
    for time in times:
        total += int(time[:-1]) * multipliers[time[-1]]
    return total


def shorten_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    time_str = ''
    if days != 1:
        time_str += f'{days} days '
    else:
        time_str += f'{days} day '
    if hours != 1:
        time_str += f'{hours} hours '
    else:
        time_str += f'{hours} hour '
    if minutes != 1:
        time_str += f'{minutes} minutes '
    else:
        time_str += f'{minutes} minute '
    if seconds != 1:
        time_str += f'{seconds} seconds '
    else:
        time_str += f'{seconds} second '
    return time_str


def is_admin(reverse=0): 
    async def predicate(ctx):
        admin_role_ids = db_funcs.get_from_guild(ctx.guild.id, 'admin_role_ids').split(' ')
        if any(str(u_role.id) in admin_role_ids for u_role in ctx.author.roles):
            return True
        elif ctx.author == ctx.guild.owner or ctx.author.id == 258306791174176770: # dunno if I should keep the id bypass
            return True

        await ctx.send('You don\'t have the required role to do this!')
        return False

    if reverse:
        return not commands.check(predicate)
    return commands.check(predicate)


command_categories = {
        'setup': 'Server setup commands',
        'moderation': 'General moderation commands',
        'all': 'Lists all of the sever commands available to you'
    }

def get_available_categories(guild, user):
    user_roles = user.roles
    a_role_ids = db_funcs.get_from_guild(guild.id, 'admin_role_ids')
    if any(str(role.id) in a_role_ids for role in user_roles):
        user_rank = 'moderation'
    elif user == guild.owner:
        user_rank = 'setup'
    else:
        user_rank = 'all'

    available_categories = {}
    categories_items = list(command_categories.items())
    for i in range(len(categories_items)):
        if categories_items[i][0] == user_rank:
            available_categories = dict(categories_items[i: ])
            break
    return available_categories

class Command(commands.Command):
    def __init__(self, *args, **kwargs):
        self.category = kwargs.pop('category')
        super().__init__(*args, **kwargs)

if __name__ == '__main__':
    time_str = '1s 17h 14m'
    print(sum(get_total_time(time_str)))