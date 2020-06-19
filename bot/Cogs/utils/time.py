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
                print('Mute dicitonary key error, skipping current time request')
    return total


def shorten_time(seconds):
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