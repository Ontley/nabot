import discord
from discord.ext import commands
import asyncio
from bot.constants import highest_admin_role_id, mute_role_id, admin_roles


class TimeoutObject:
    def __init__(self, user_origin, channel, mute_time=120):
        self.user_origin = user_origin
        self.channel = channel # debug purposes
        self.mute_role = channel.guild.get_role(mute_role_id)
        self.log_channel = channel.guild.system_channel
        self.mute_time = mute_time
        print(f'\n        constructed timeout in {channel} by {user_origin}\n')

    async def log(self, user, reversed=False):
        string = f'{user}'
        if not reversed:
            string += f'muted by timeout in {self.channel}'
        else:
            string += f'muted by uno reverse in {self.channel}'
        await self.log_channel.send(string)

    async def execute(self, target, uno_reverse = 0):
        if not uno_reverse:
            print(f'\n        {target.display_name} timed out\n')
            await self.channel.send(f'{target} got fucked')
        else:
            print(f'\n        {target.display_name} reversed\n')
            await self.channel.send(f'{target} got uno reversed')
        await target.add_roles(self.mute_role)
        await asyncio.sleep(self.mute_time)
        await target.remove_roles(self.mute_role)


def is_not_admin():
    def predicate(ctx):
        if ctx.author.top_role > ctx.guild.get_role(highest_admin_role_id):
            return True
        else:
            print(f'\n      bypass for {ctx.author.display_name}\n')
            return False
    return commands.check(predicate)


class Timeout(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.timeouts = {}

    @commands.command()
    async def timeout(self, ctx):
        message = ctx.message
        channel = message.channel
        if message.author.id != self.client.user.id:
            timeout = TimeoutObject(message.author, channel)
            try:
                self.timeouts[channel].append(timeout)
            except:
                self.timeouts[channel] = [timeout]

            def check(message):
                return message.content in {'++unoreverse', '++reverse'} and message.channel == channel
            try:
                await self.client.wait_for('message', check=check, timeout=7)
                if channel in self.timeouts:
                    if self.timeouts[channel]:
                        await self.timeouts[channel][0].execute(timeout.user_origin, reverseflag = 1)
                        del self.timeouts[channel][0]

            except asyncio.TimeoutError:
                print('\n       TIMEOUT: REVERSE EXPIRED\n')

    @commands.command(aliases = ['reverse'])
    async def unoreverse(self, ctx):
        try:
            if not self.timeouts[ctx.message.channel]:
                await ctx.send('No timeouts available to reverse')
        except KeyError:
            await ctx.send('No timeouts available to reverse')

    @commands.Cog.listener()
    @is_not_admin()
    async def on_message(self, message):
        if message.author != self.client.user:
            channel = message.channel

            # This mutes the next person if the message isn't a command

            if channel in self.timeouts:
                if self.timeouts[channel]:
                    for i in range(len(self.timeouts[channel])):
                        if message.author != self.timeouts[channel][i].user_origin:
                            await self.timeouts[channel][i].execute(message.author)
                            del self.timeouts[channel][i]
                        else:
                            print(f'own bypass for {message.author.display_name}')

def setup(client):
    client.add_cog(Timeout(client))