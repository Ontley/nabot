import datetime

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
                print('Mute dictionary key error, skipping current time request')
    return total


def shorten_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    time_str = ''
    if days > 1:
        time_str += f'{days} days '
    else:
        time_str += f'{days} day '
    if hours > 1:
        time_str += f'{hours} hours '
    else:
        time_str += f'{hours} hour '
    if minutes > 1:
        time_str += f'{minutes} minutes '
    else:
        time_str += f'{minutes} minute '
    if seconds > 1:
        time_str += f'{seconds} seconds '
    else:
        time_str += f'{seconds} second '
    return time_str