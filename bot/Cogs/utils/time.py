import datetime
from re import findall


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