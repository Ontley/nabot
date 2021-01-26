import discord
from discord.ext import commands
from discord.utils import get
import asyncio
from bot.Cogs.utils import db_funcs
from math import ceil
from bot.Cogs.utils.utils import get_available_categories, command_categories, Command


def get_user_rank(guild, user):
    user_roles = user.roles
    a_role_ids = db_funcs.get_from_guild(guild.id, 'admin_role_ids')
    if any(str(role.id) in a_role_ids for role in user_roles):
        return 'Moderation'
    elif user == guild.owner:
        return 'Setup'
    return 'All'


class HelpObject():
    def __init__(self, ctx, title, fields, page):
        self.ctx = ctx
        self.bot = ctx.bot
        self.author_id = ctx.author.id
        self.title = title
        self.fields = list(fields.items())
        self.num_pages = ceil(len(fields) / 5)
        self.page = page
        self.embed = self.make_embed(page)

    def make_embed(self, page):
        self.page = page
        embed_fields = self.fields[(page-1)*5: page*5]
        help_embed = discord.Embed()
        if self.title is not None:
            help_embed.title = self.title
        help_embed.colour = 16747116
        help_embed.set_author(
            name=str(self.bot.user),
            icon_url=self.bot.user.avatar_url
        )
        help_embed.set_footer(text=f'{page}/{self.num_pages}')
        for field_name, field_value in embed_fields:
            help_embed.add_field(
                name=field_name, value=field_value, inline=False)
        return help_embed

    async def send_help_msg(self):
        '''Sends the help object's embed'''
        self.message = await self.ctx.send(embed=self.embed)
        if self.num_pages > 1:
            for emoji in ["⏪", "◀", "▶", "⏩"]:
                await self.message.add_reaction(emoji)

    async def edit(self, new_page):
        '''Edits the message embed with a newly created one, used in page control system'''
        new_embed = self.make_embed(new_page)
        await self.message.edit(embed=new_embed)


class Help(commands.Cog):
    '''Help commands category'''

    def __init__(self, client):
        self.client = client
        self.help_messages = {}

    @commands.command(category='all', cls=Command)
    async def help(self, ctx, arg=None, page=1):
        '''Sends a list of all the server command, commands from a specific category or details of a specific command
        Usage:
        `{prefix}help Miscellaneous`
        `{prefix}help poll`'''
        if ctx.author.id in self.help_messages:
            help_obj = self.help_messages[ctx.author.id]
            await help_obj.message.delete()

        prefix = db_funcs.get_from_guild(ctx.guild.id, 'prefix')
        available_categories = get_available_categories(ctx.guild, ctx.author)
        all_commands = list(ctx.bot.all_commands.values())

        if arg is None:
            if len(available_categories) > 1:
                title = 'Server command categories'
                embed_fields = {category.capitalize(
                ): description for category, description in available_categories.items()}
            else:
                try:
                    arg = list(available_categories.keys())[0]
                except IndexError:
                    print('user doesn\'t have available categories to view??')

        if arg is not None:
            arg = arg.lower()
            if arg == 'all':
                title = 'Showing all available server commands'
                embed_fields = {com.name: com.help.format(
                    prefix=prefix) for com in all_commands if com.category in available_categories}

            elif arg in available_categories:
                title = f'Commands from the category {arg.capitalize()}'
                embed_fields = {}
                for comm in all_commands:
                    if comm.category == arg:
                        embed_fields[comm.name] = comm.help.format(
                            prefix=prefix)

            elif arg in command_categories and arg not in available_categories:
                await ctx.send('You do not have permission to view this set of commands')
                return

            elif (command := get(all_commands, name=arg)) is not None:
                title = None
                if command.category not in available_categories:
                    await ctx.send('You do not have permission to view this command')
                    return
                embed_fields = {
                    command.name: command.help.format(prefix=prefix)}

            else:
                await ctx.send(f'{arg} is not a valid command or command category')
                return

        help_obj = HelpObject(ctx, title, embed_fields, page)
        self.help_messages[ctx.author.id] = help_obj
        await help_obj.send_help_msg()

        await help_obj.message.add_reaction('🗑')

        def check(reaction, user):
            return str(reaction) == '🗑' and user == ctx.author and reaction.message == help_obj.message
        try:
            await self.client.wait_for('reaction_add', check=check, timeout=180)
            await help_obj.message.delete()
            del self.help_messages[ctx.author.id]
        except asyncio.TimeoutError:
            await help_obj.message.clear_reactions()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        '''Page control system through reactions'''
        emoji = str(payload.emoji)
        member = payload.member

        if member.id in self.help_messages:
            help_obj = self.help_messages[member.id]
            emoji_page_dict = {"⏪": 1,
                               "◀": help_obj.page-1,
                               "▶": help_obj.page+1,
                               "⏩": help_obj.num_pages
                               }

            if emoji in emoji_page_dict:
                new_page = emoji_page_dict[emoji]
                if new_page > help_obj.num_pages:
                    new_page = help_obj.num_pages
                elif new_page < 1:
                    new_page = 1

                await help_obj.edit(new_page)
                await help_obj.message.remove_reaction(emoji, member)


def setup(client):
    client.add_cog(Help(client))
