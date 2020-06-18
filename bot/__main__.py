import discord
from discord.ext import commands
from random import choice
import json
import asyncio
from re import findall, match
from os import getcwd, listdir
from os.path import isdir


client = commands.Bot(command_prefix = '++')
client.remove_command('help')

def get_extensions(directory):
    extensions = []
    for entry in listdir(directory):
        if not entry.startswith('__'):
            entry_path = f'{directory}/{entry}'
            if isdir(entry_path):
                extensions += get_extensions(entry_path)
            else:
                extensions.append(entry.rstrip('.py'))
    return extensions

print(get_extensions('./bot/Cogs'))
# for extension in extensions:
#     client.load_extension(f'bot.Cogs.{extension}')

# client.run('NzE1MTg0MjQ2NzYzMDI4NTky.Xs5n6w.f_DAY0zPVW1sHKeOx7PoqpVguAE')
