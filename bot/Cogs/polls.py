import discord
from discord.ext import commands
from bot.Cogs.utils import time
from re import findall
from bot.constants import admin_roles, NUMBER_EMOJIS
import asyncio


class Poll:
    def __init__(self, title, options, _id, author, channel, duration, anon, allow_multi): # info is a shit var, fix it
        self._id = _id
        self.options = options
        self.votes = {i: 0 for i in range(len(self.options))}
        self.author = author
        self.channel = channel
        self.duration = duration
        self.active = True
        self.anon = anon
        self.allow_multi = allow_multi
        self.user_votes = {}
        embed = discord.Embed(
            title = f'Question: {title}',
            description = f'Lasts for {time.shorten_time(duration)}\nid {_id}',
            colour = 16747116
            )
        embed.set_author(
            name=f'Poll created by {author.display_name}',
            icon_url=author.avatar_url
            )

        for index, option in enumerate(self.options):
            embed.add_field(name=f'Option {index+1}', value=f'{option}', inline=False)
        self.embed = embed


    async def add_vote(self, user, option_id):
        if self.allow_multi:
            if user.id in self.user_votes:
                if option_id in self.user_votes[user.id]:
                    print(f'User {user.display_name} already voted for option {option_id + 1}')
                    return

                else:
                    self.user_votes[user.id].append(option_id)
            else:
                self.user_votes[user.id] = [option_id]

        else:
            if user.id in self.user_votes:
                print(f'Poll doesn\'t allow multivote, user {user.display_name} already voted')
                return
            else:
                self.user_votes[user.id] = option_id


    async def send_poll(self):
        await self.channel.send(embed = self.embed)
        self.message = self.channel.last_message
        if len(self.options) <= 10:
            for i in range(len(self.options)):
                await self.message.add_reaction(NUMBER_EMOJIS[i])


    async def end(self):
        pass


class Polls(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.active_polls = {}

    @commands.command(aliases=['poll'])
    async def makepoll(self, ctx):
        if ctx.author.id in self.active_polls:
            await ctx.send(f'{ctx.author.display_name}, you already have a poll active')
            return
        if len(self.active_polls) >= 3:
            await ctx.send('Too many polls active in the server')
            return

        msgtext = ctx.message.content
        info = findall(r"\"[\w\d ?!.,:;]+\"", msgtext)
        info = [element.strip('"') for element in info]
        title = info[0]
        options = set(info[1: ])
        times = findall(r'\d+[smhd]{1}', msgtext)
        if times:
            duration = time.get_total_time(times)
        else:
            duration = 360

        anon = '-a' in msgtext or '-anon' in msgtext
        allow_multi = '-m' in msgtext or '-multiple' in msgtext
        poll = Poll(title, options, ctx.message.id,  ctx.author, ctx.channel, duration, anon, allow_multi)
        await poll.send_poll()
        self.active_polls[ctx.author.id] = poll
        await asyncio.sleep(poll.duration)
        await poll.end()
        if ctx.author.id in self.active_polls: # poll can be deleted early, so need a check to not get error
            del self.active_polls[ctx.author.id]

    @commands.command()
    async def endpoll(self, ctx):
        if ctx.author.id not in self.active_polls:
            await ctx.send(f'{ctx.author.display_name}, you don\'t have an active poll')
            return

        await ctx.send('Ending poll early')
        poll = self.active_polls[ctx.author.id]
        await poll.end()
        del self.active_polls[ctx.author.id]

    @commands.command()
    @commands.has_any_role(*admin_roles)
    async def forceend(self, ctx, _id):
        _id = int(_id)
        for _, poll in self.active_polls.items():
            print(f'{poll._id}\n{_id}\n{poll._id == _id}')
            if poll._id == _id:
                await poll.end()
                await ctx.send(f'admin force poll {_id} to end early')
                del self.active_polls[poll.author.id]
                break
        else:
            await ctx.send(f'Poll with id {_id} not found')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        emoji = str(payload.emoji)
        for _, poll in self.active_polls.items():
            if payload.message_id == poll._id:
                if len(poll.options) <= 10:
                    if emoji in NUMBER_EMOJIS:
                        emoji_index = NUMBER_EMOJIS.index(emoji)
                        poll.add_vote(payload.member, emoji_index)
                        break


def setup(client):
    client.add_cog(Polls(client))