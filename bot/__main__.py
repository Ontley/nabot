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
        if not entry.startswith('__') and entry != 'utils':
            entry_path = f'{directory}/{entry}'
            if isdir(entry_path):
                extensions += get_extensions(entry_path)
            else:
                extensions.append(entry_path.rstrip('.py'))
    return extensions

cogs = get_extensions('./bot/Cogs')
for entry in cogs:
    cog = entry.replace("/", ".").lstrip(".")
    client.load_extension(f'{cog}')

with open('token.txt', 'r') as token_file:
    token = token_file.readlines().strip()
    client.run(token)
