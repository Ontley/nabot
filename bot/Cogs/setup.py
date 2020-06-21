import sqlite3
import discord
from discord.ext import commands

class Setup(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        '''if the bot restarts, running infraction timers are lost so tempmutes and tempbans would break
        this reapplies all active infractions for servers the bot is in'''
        
        # database stuff

        # apply found infractions

        pass # remove this

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.send(f'Command {ctx.command.name} not found')

def setup(client):
    client.add_cog(Setup(client))