import discord
from discord.ext import commands
import json
from random import choice


class MiscUtils(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.dick_sizes = ['smol', 'non-existant', 'tiny', 'MEGA DONG', 'big']

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Pong! {self.client.latency*1000}ms')

    @commands.command()
    async def dicksize(self, ctx):
        await ctx.send(f'{choice(self.dick_sizes)} schlong')

    @commands.command()
    async def nwords(self, ctx):
        message = ctx.message
        mentions = message.mentions
        targets = [mtn for mtn in mentions] if mentions else [message.author]

        filepath = 'C:/Users/leola/Desktop/Leo/Coding/Python/DISCORD_BOT/nWordCount.json'
        with open(filepath, 'r') as json_file:
            nword_count = json.load(json_file)

        for targ in targets:
            if targ in nword_count:
                nwords = nword_count[targ.id]
                await ctx.send(f'{targ.display_name} said the n-word {nwords} times')
            else:
                await ctx.send(f'{targ.display_name} ain\'t even said the n-word')

    @commands.command(aliases = ['neisplatise'])
    async def isplatise(self, ctx):
        filename = 'ne_isplati_se' if 'ne' in ctx.message.content else 'isplati_se'
        with open(f'C:/Users/leola/Desktop/Leo/mememememe/{filename}.png', 'rb') as image:
            img_file = discord.File(image)
        await ctx.send(file=img_file)

    @commands.Cog.listener()
    async def on_message(self, message):
        msgtext = message.content

        if message.author != self.client.user:
            '''
            The n-word counter
            '''
            if 'nigga' in msgtext or 'nigger' in msgtext:
                user = str(message.author.id)
                filepath = 'C:/Users/leola/Desktop/Leo/Coding/Python/DISCORD_BOT/nWordCount.json'
                with open(filepath, 'r') as json_file:
                    nword_count = json.load(json_file)
                    if user in nword_count: 
                        nword_count[user] += msgtext.count('nigga') + msgtext.count('nigger')
                    else:
                        nword_count[user] = msgtext.count('nigga') + msgtext.count('nigger')

                with open(filepath, 'w') as json_file:
                    json_file.write(json.dumps(nword_count))

            if msgtext == 'black lives matter':
                user = str(message.author.id)
                filepath = 'C:/Users/leola/Desktop/Leo/Coding/Python/DISCORD_BOT/nWordCount.json'
                with open(filepath, 'r') as json_file:
                    nword_count = json.load(json_file)
                    if user in nword_count: 
                        nword_count[user] -= 1
                    else:
                        nword_count[user] = -1

                with open(filepath, 'w') as json_file:
                    json_file.write(json.dumps(nword_count))


def setup(client):
    client.add_cog(MiscUtils(client))