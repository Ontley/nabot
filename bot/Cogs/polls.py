import discord
from discord.ext import commands
from bot.Cogs.utils.utils import is_admin, shorten_time, Command
from re import findall
from bot.constants import NUMBER_EMOJIS
import asyncio


class Poll:
    '''Poll object because there's a lot here'''

    def __init__(self, title, options, _id, author, channel, duration, anon, allow_multi):
        self.id = _id
        self.title = title
        self.options = options
        self.options_stats = {i: 0 for i in range(len(self.options))}
        self.author = author
        self.channel = channel
        self.duration = duration
        self.anon = anon
        self.allow_multi = allow_multi
        self.all_votes = {}
        self.total_votes = 0
        embed = discord.Embed(
            title=f'Question: {title}',
            description=f'Lasts for {shorten_time(duration)}\nid {_id}',
            colour=16747116
        )
        embed.set_author(
            name=f'Poll created by {author.display_name}',
            icon_url=author.avatar_url
        )

        for index, option in enumerate(self.options):
            embed.add_field(
                name=f'Option {index+1}', value=f'{option}', inline=False)
        self.embed = embed

    async def add_vote(self, user, option):
        '''Handles all of the voting, anonymous and multivote stuff'''
        if self.allow_multi:
            if user.id in self.all_votes:
                if option in self.all_votes[user.id]:
                    print(
                        f'User {user.display_name} already voted for option {option}')
                    return

                else:
                    self.all_votes[user.id].append(option)
                    self.options_stats[option] += 1
                    self.total_votes += 1
            else:
                self.all_votes[user.id] = [option]
                self.options_stats[option] += 1
                self.total_votes += 1

        else:
            if user.id in self.all_votes:
                print(
                    f'Poll doesn\'t allow multivote, user {user.display_name} already voted')
                return
            else:
                self.all_votes[user.id] = [option]
                self.options_stats[option] += 1
                self.total_votes += 1

    async def remove_vote(self, user_id, option):
        self.all_votes[user_id].remove(option)
        self.options_stats[option] -= 1
        self.total_votes -= 1

    async def send_poll(self):
        '''Sends the poll in it's channel'''
        self.message = await self.channel.send(embed=self.embed)
        if len(self.options) <= 10:
            for i in range(len(self.options)):
                await self.message.add_reaction(NUMBER_EMOJIS[i])

    async def end(self):
        '''Ends the poll, sending an embed with the results'''
        end_embed = discord.Embed(
            title=f'Poll ended: {self.title}',
            colour=16747116
        )
        end_embed.set_author(
            name=f'Poll created by {self.author.display_name}',
            icon_url=self.author.avatar_url
        )

        for i in range(len(self.options)):
            option_votes = self.options_stats[i]
            try:
                option_percentage = option_votes/self.total_votes
            except ZeroDivisionError:
                option_percentage = 0

            end_embed.add_field(
                name=f'Option {i+1} ({option_votes} votes, {option_percentage}%)',
                value=self.options[i],
                inline=False
            )
        await self.channel.send(embed=end_embed)


class Polls(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.active_polls = {}

    async def poll_handler(self, poll, ctx):
        '''Sends the poll made and creates the timers for it'''
        await poll.send_poll()
        self.active_polls[ctx.author.id] = poll
        await asyncio.sleep(poll.duration)
        if poll in list(self.active_polls.values()):
            await poll.end()
            del self.active_polls[ctx.author.id]

    @commands.command(category='all', cls=Command)
    async def poll(self, ctx):
        '''Creates a poll lasting 10 minutes
        Usage:
        `{prefix}poll "This is the title" "Options one" "Options two"`'''
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
        options = info[1: 11]
        duration = 600
        anon = '-a' in msgtext or '-anon' in msgtext
        allow_multi = '-m' in msgtext or '-multiple' in msgtext
        poll = Poll(title, options, ctx.message.id,  ctx.author,
                    ctx.channel, duration, anon, allow_multi)
        await self.poll_handler(poll, ctx)

    @commands.command(category='all', cls=Command)
    async def endpoll(self, ctx):
        '''Allows the poll's creator to end the poll before it's timer stops
        Usage:
        `{prefix}endpoll`'''
        if ctx.author.id not in self.active_polls:
            await ctx.send(f'{ctx.author.display_name}, you don\'t have an active poll')
            return

        poll = self.active_polls[ctx.author.id]
        await poll.end()
        del self.active_polls[ctx.author.id]

    @commands.command(category='moderation', cls=Command)
    @is_admin()
    async def forceend(self, ctx, poll_id):
        '''Allows an admin to force end a poll given it's ID
        Usage:
        `{prefix}forceend 726826227717111818`'''
        try:
            poll_id = int(poll_id)
        except ValueError:
            await ctx.send(f'The argument passed is not a number')
        for _, poll in self.active_polls.items():
            if poll.id == poll_id:
                await poll.end()
                await ctx.send(f'admin force poll {poll_id} to end early')
                del self.active_polls[poll.author.id]
                break
        else:
            await ctx.send(f'Poll with id {poll_id} not found')

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        '''Adds a vote to the poll where the reaction was added'''
        if payload.member != self.client.user:
            emoji = str(payload.emoji)
            for poll in list(self.active_polls.values()):
                if payload.message_id == poll.message.id:
                    if emoji in NUMBER_EMOJIS:
                        emoji_index = NUMBER_EMOJIS.index(emoji)
                        await poll.add_vote(payload.member, emoji_index)
                        break

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        '''Removes the user's vote'''
        emoji = str(payload.emoji)
        for poll in list(self.active_polls.values()):
            if payload.message_id == poll.message.id:
                if emoji in NUMBER_EMOJIS:
                    emoji_index = NUMBER_EMOJIS.index(emoji)
                    await poll.remove_vote(payload.member.id, emoji_index)
                    break


def setup(client):
    client.add_cog(Polls(client))
