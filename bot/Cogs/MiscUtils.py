import discord
from discord.ext import commands
import json
from random import choice
from os import getcwd
from bot.Cogs.utils.utils import command_categories, Command


class Miscellaneous(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.dick_sizes = ['smol', 'non-existant', 'tiny', 'MEGA DONG', 'big']
        self.nword_filepath = f'{getcwd()}/nWordCount.json'

    @commands.command(category='all', cls=Command)
    async def ping(self, ctx):
        '''Sends the bot's heartbeat latency in miliseconds
        Usage:
        `{prefix}ping`'''
        await ctx.send(f'Pong! {round(self.client.latency*1000)}ms')

    @commands.command(category='all', cls=Command)
    async def dicksize(self, ctx):
        '''Sends the true size of your schlong
        Usage:
        `{prefix}dicksize`'''
        await ctx.send(f'{choice(self.dick_sizes)} schlong')

    @commands.command(category='all', cls=Command)
    async def nwords(self, ctx):
        '''Command that allows you to check how many times users have said the nword, or your own count
        Usage:
        `{prefix}nwords 258306791174176770 220992189830922241`'''
        message = ctx.message
        mentions = message.mentions
        targets = [mtn for mtn in mentions] if mentions else [message.author]

        filepath = f'{getcwd()}/nWordCount.json'
        with open(filepath, 'r') as json_file:
            nword_count = json.load(json_file)

        for targ in targets:
            if targ in nword_count:
                nwords = nword_count[targ.id]
                await ctx.send(f'{targ.display_name} said the n-word {nwords} times')
            else:
                await ctx.send(f'{targ.display_name} ain\'t even said the n-word')

    @commands.command(aliases = ['neisplatise'], category='all', cls=Command)
    async def isplatise(self, ctx):
        '''Sends the isplati se image
        Usage:
        `{prefix}isplatise`
        `{prefix}neisplatise` - invereted colors'''
        filename = 'ne_isplati_se' if 'ne' in ctx.message.content else 'isplati_se'
        with open(f'C:/Users/leola/Desktop/Leo/mememememe/{filename}.png', 'rb') as image:
            img_file = discord.File(image)
        await ctx.send(file=img_file)

    @commands.Cog.listener()
    async def on_message(self, message):
        msgtext = message.content
        if message.author != self.client.user:
            '''The n-word counter, TODO: set this up as db logic'''
            if 'nigga' in msgtext or 'nigger' in msgtext:
                user = str(message.author.id)
                with open(self.nword_filepath, 'r') as json_file:
                    nword_count = json.load(json_file)
                    if user in nword_count: 
                        nword_count[user] += msgtext.count('nigga') + msgtext.count('nigger')
                    else:
                        nword_count[user] = msgtext.count('nigga') + msgtext.count('nigger')

                with open(self.nword_filepath, 'w') as json_file:
                    json_file.write(json.dumps(nword_count))

            if msgtext == 'black lives matter':
                '''Removes one from your nword counter if you truly support BLM TODO: set up as db logic'''
                user = str(message.author.id)
                with open(self.nword_filepath, 'r') as json_file:
                    nword_count = json.load(json_file)
                    if user in nword_count: 
                        nword_count[user] -= 1
                    else:
                        nword_count[user] = -1

                with open(self.nword_filepath, 'w') as json_file:
                    json_file.write(json.dumps(nword_count))


def setup(client):
    client.add_cog(Miscellaneous(client))