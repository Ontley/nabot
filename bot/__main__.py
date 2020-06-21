import discord
from discord.ext import commands
from os import listdir
from os.path import isdir


client = commands.Bot(command_prefix = '++')
client.remove_command('help')

def get_extensions(directory):
    '''Gets a list of the cogs'''
    extensions = []
    for entry in listdir(directory):
        if not entry.startswith('__') and entry != 'utils':
            entry_path = f'{directory}/{entry}'
            if isdir(entry_path):
                extensions += get_extensions(entry_path)
            else:
                extensions.append(entry_path[: -3])
    return extensions

'''Loads cogs'''
cogs = get_extensions('./bot/Cogs')
for entry in cogs:
    cog = entry.replace("/", ".").lstrip(".")
    client.load_extension(f'{cog}')

with open('token.txt', 'r') as token_file:
    token = token_file.readlines()[0].strip()
client.run(token)
