import discord
import sqlite3
from discord.ext import commands
from os import listdir
from os.path import isdir
from bot.Cogs.utils import db_funcs


'''Creates all the db tables necessary for the bot if they don't already exist'''
db_funcs.create_tables()

async def get_prefix(client, message):
    return db_funcs.get_from_guild(message.guild.id, 'prefix')

client = commands.Bot(command_prefix = get_prefix)
client.remove_command('help')

def get_extensions(directory):
    '''Gets a list of the cogs from the bot/Cogs folder'''
    extensions = []
    for entry in listdir(directory):
        if not entry.startswith('__') and entry != 'utils':
            entry_path = f'{directory}/{entry}'
            if isdir(entry_path):
                extensions += get_extensions(entry_path)
            else:
                extensions.append(entry_path[: -3])
    return extensions

cogs = get_extensions('./bot/Cogs')
for entry in cogs:
    cog = entry.replace("/", ".").lstrip(".")
    client.load_extension(f'{cog}')


# client.load_extension('bot.Cogs.setup')
# client.load_extension('bot.Cogs.Moderation.infractions')
# client.load_extension('bot.Cogs.CustomHelpCommand')


with open('token.txt', 'r') as token_file:
    token = token_file.readlines()[0].strip()
client.run(token)
