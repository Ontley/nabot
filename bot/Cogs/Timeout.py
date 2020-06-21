import discord
from discord.ext import commands
import asyncio
from bot.constants import highest_admin_role_id, mute_role_id, admin_roles


'''Explanation: if the command timeout is activated, any person that sends ANY message into that channel will get muted
BUT: if the command reverse or unoreverse is sent in the short period (can be set) after the timeout command, the person that started the timeout gets muted'''

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
        '''Executes, mutes the person that was specified, uno_reverse bool for different messages on execute'''
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
    '''Custom broken decorator '''
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
        self.timeouts_count = {}

    @commands.command()
    async def timeout(self, ctx):
        '''Creates the timeout object, TODO: move handling stuff to own function'''
        message = ctx.message
        channel = message.channel
        if message.author.id != self.client.user.id:
            if message.author.id in self.timeouts_count:
                if self.timeouts_count[message.author.id] < 3:
                    timeout_obj = TimeoutObject(message.author, channel)
                    self.timeouts[channel].append(timeout_obj)
                    self.timeouts_count[message.author.id] += 1
                    print(self.timeouts_count[message.author.id])
                else:
                    await ctx.send(f'You already have 3 timeouts active')
            else:
                timeout_obj = TimeoutObject(message.author, channel)
                self.timeouts[channel] = [timeout_obj]
                self.timeouts_count[message.author.id] = 1

            def check(message):
                return (message.content in {'++unoreverse', '++reverse'}
                        and message.channel == channel)
            try:
                await self.client.wait_for('message', check=check, timeout=7)
                if channel in self.timeouts:
                    if self.timeouts[channel]:
                        timeout_obj = self.timeouts[channel][0]
                        await timeout_obj.execute(timeout_obj.user_origin, reverseflag = 1)
                        self.timeouts_count[timeout_obj.user_origin.id] -= 1
                        del self.timeouts[channel][0]

            except asyncio.TimeoutError:
                print('\n       TIMEOUT: REVERSE EXPIRED\n')

    @commands.command(aliases = ['reverse'])
    async def unoreverse(self, ctx):
        '''Handles cases where reverse/unoreverse command is sent before after expiry or after execution'''
        try:
            if not self.timeouts[ctx.message.channel]:
                await ctx.send('No timeouts available to reverse')
        except KeyError:
            await ctx.send('No timeouts available to reverse')

    @commands.Cog.listener()
    @is_not_admin()
    async def on_message(self, message):
        '''Executes the timeout if someone sends a message in the channel'''
        if message.author != self.client.user:
            channel = message.channel
            if channel in self.timeouts:
                if self.timeouts[channel]:
                    for i, timeout_obj in enumerate(self.timeouts[channel]):
                        if message.author != timeout_obj.user_origin:
                            del self.timeouts[channel][i]
                            await timeout_obj.execute(message.author)
                            self.timeouts_count[timeout_obj.user_origin.id] -= 1
                            break
                        else:
                            print(f'own bypass for {message.author.display_name}')

def setup(client):
    client.add_cog(Timeout(client))