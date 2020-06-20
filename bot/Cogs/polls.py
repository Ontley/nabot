import discord
from discord.ext import commands
from bot.Cogs.utils import time
from re import findall
from bot.constants import admin_roles, NUMBER_EMOJIS
import asyncio


class Poll:
    def __init__(self, title, options, _id, author, channel, duration, anon, allow_multi):
        self._id = _id
        self.title = title
        self.options = options
        self.author = author
        self.channel = channel
        self.duration = duration
        self.anon = anon
        self.allow_multi = allow_multi
        self.all_votes = {}
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

    async def add_vote(self, user, option):
        if option not in self.options:
            if option > len(self.options):
                if not self.anon:
                    await self.channel.send(f'The option {option} doesn\'t exist')
                    return

        if self.allow_multi:
            if user.id in self.all_votes:
                if option in self.all_votes[user.id]:
                    print(f'User {user.display_name} already voted for option {option}')
                    return

                else:
                    self.all_votes[user.id].append(option)
            else:
                self.all_votes[user.id] = [option]

        else:
            if user.id in self.all_votes:
                print(f'Poll doesn\'t allow multivote, user {user.display_name} already voted')
                return
            else:
                self.all_votes[user.id] = [option]


    async def send_poll(self):
        await self.channel.send(embed = self.embed)
        self.message = self.channel.last_message
        if len(self.options) <= 10:
            for i in range(len(self.options)):
                await self.message.add_reaction(NUMBER_EMOJIS[i])


    async def end(self):
        total_votes = sum([len(votes) for votes in list(self.all_votes.values())])
        options_stats = {i: {'votes': 0, 'percent': 0} for i in range(len(self.options))}

        for user_votes in list(self.all_votes.values()):
            for vote in user_votes:
                options_stats[vote]['votes'] += 1

        for i in range(len(options_stats)):
            option_votes = options_stats[i]['votes']
            try:
                options_stats[i]['percent'] = option_votes/total_votes*100
            except ZeroDivisionError:
                options_stats[i]['percent'] = 0

        end_embed = discord.Embed(
            title = f'Poll ended: {self.title}',
            colour = 16747116
            )
        end_embed.set_author(
            name=f'Poll created by {self.author.display_name}',
            icon_url=self.author.avatar_url
            )
        
        for i in range(len(self.options)):
            option_votes = options_stats[i]['votes']
            option_percentage = options_stats[i]['percent']
            end_embed.add_field(
                name = f'Option {i+1} ({option_votes} votes, {option_percentage}%)',
                value = self.options[i],
                inline = False
            )
        await self.channel.send(embed=end_embed)


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
        options = info[1: ]
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
        if ctx.author.id in self.active_polls:
            await poll.end()
            del self.active_polls[ctx.author.id]

    @commands.command()
    async def endpoll(self, ctx):
        if ctx.author.id not in self.active_polls:
            await ctx.send(f'{ctx.author.display_name}, you don\'t have an active poll')
            return

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
        if payload.member != self.client.user:
            emoji = str(payload.emoji)
            for poll in list(self.active_polls.values()):
                if payload.message_id == poll.message.id:
                    if len(poll.options) <= 10:
                        if emoji in NUMBER_EMOJIS:
                            emoji_index = NUMBER_EMOJIS.index(emoji)
                            await poll.add_vote(payload.member, emoji_index)
                            break

    @commands.command()
    async def vote(self, ctx, _id, option):
        for poll in list(self.active_polls.values()):
            if poll._id == _id:
                if poll.anon:
                    ctx.message.delete()
                await poll.add_vote(ctx.author, option)


def setup(client):
    client.add_cog(Polls(client))