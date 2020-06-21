import discord
from discord.ext import commands
import asyncio
import json
from bot.constants import admin_roles
from os import getcwd

class HelpObject():
    def __init__(self, ctx, category_name, command_class, page, num_pages):
        self.user_activated = ctx.message.author
        self.category_name = category_name
        self.page = page
        self.ctx = ctx
        self.command_class = command_class
        self.num_pages = num_pages
        self.embed = self.make_embed(command_class, page)

    def make_embed(self, commands_dict, page):
        '''Makes the embed with the dictionary given by initialization'''
        help_commands_dict = commands_dict[f'Page {page}']
        help_commands_dict["author"]["name"] = self.ctx.me.display_name
        help_commands_dict["footer"]["text"] = f'{page}/{self.num_pages}'

        embed = discord.Embed.from_dict(help_commands_dict)
        if self.category_name == 'empty' and self.ctx.author.top_role.name in admin_roles:
            embed.add_field(name='Admin Commands', value='`++help admin`\nLists available admin commands')
        return embed

    async def send_help_msg(self):
        '''Sends the help object's embed'''
        await self.ctx.send(embed=self.embed)
        self.message = self.ctx.channel.last_message
        if self.num_pages > 1:
            for emoji in ["⏪", "◀", "▶", "⏩"]:
                await self.message.add_reaction(emoji)

    async def edit(self, new_page):
        '''Edits the message embed with a newly created one, used in page control system'''
        new_embed = self.make_embed(self.command_class, new_page)
        await self.message.edit(embed=new_embed)


class CustomHelpCommand(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.help_messages = {}

    @commands.command()
    async def help(self, ctx, command_class = 'empty', page = 1):
        if ctx.author.top_role.name not in admin_roles and command_class == 'admin':
            await ctx.send(f'You are not permitted to view this category')
        else:
            with open(f"{getcwd()}/help_commands_file.json", 'r') as help_file:
                commands_categories = json.load(help_file)
                try:
                    commands_dict = commands_categories[command_class]

                    num_pages = len(commands_dict)
                    if page > num_pages:
                        page = num_pages
                    elif page < 1:
                        page = 1

                    help_obj = HelpObject(ctx, command_class, commands_dict, page, num_pages)

                    '''TODO: help_object_handler function for code below'''
                    self.help_messages[ctx.author.id] = help_obj
                    await help_obj.send_help_msg()

                    await help_obj.message.add_reaction('🗑')
                    def check(reaction, user):
                        return str(reaction) == '🗑' and user == help_obj.ctx.author
                    try:
                        await self.client.wait_for('reaction_add', check=check, timeout=180)
                        await help_obj.message.delete()
                    except asyncio.TimeoutError:
                        await help_obj.message.clear_reactions()

                except KeyError:
                    await ctx.send(f'Command class {command_class} not found!')


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
                                "⏩":help_obj.num_pages
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
    client.add_cog(CustomHelpCommand(client))