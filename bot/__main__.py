import discord
from discord.ext import commands
from random import choice
import json
import asyncio
from re import findall, match
import os


client = commands.Bot(command_prefix = '++')
client.remove_command('help')

extensions = []
for extension in os.listdir("./bot/Cogs"):
    if not extension.startswith('__') and extensions != 'BotConstants.py':
        extensions.append(extension.rstrip('.py'))

for extension in extensions:
    client.load_extension(f'bot.Cogs.{extension}')

client.run('NzE1MTg0MjQ2NzYzMDI4NTky.Xs5n6w.f_DAY0zPVW1sHKeOx7PoqpVguAE')
