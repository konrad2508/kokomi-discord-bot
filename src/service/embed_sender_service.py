import nextcord
from nextcord.ext import commands

from colours import Colours
from embed_titles import EmbedTitles
from model.reaction.emote import Emote
from model.reaction.gif import Gif


class EmbedSenderService:
    '''Class responsible for sending preset embeds.'''

    async def send_success(self, ctx: commands.Context, message: str) -> None:
        '''Sends an embed indicating a success.'''

        embed = (nextcord.Embed(colour=nextcord.Colour.from_rgb(*Colours.SUCCESS))
                .add_field(name=EmbedTitles.OK, value=f'**{message}**'))

        await ctx.send(content=None, embed=embed)
    
    async def send_error(self, ctx: commands.Context, message: str) -> None:
        '''Sends an embed indicating an error.'''

        embed = (nextcord.Embed(colour=nextcord.Colour.from_rgb(*Colours.ERROR))
                .add_field(name=EmbedTitles.ERROR, value=f'**{message}**'))

        await ctx.send(content=None, embed=embed)

    async def send_help(self, ctx: commands.Context, commands: list[tuple[str, str]]) -> None:
        '''Sends an embed representing a help message.'''

        embed = nextcord.Embed(title=EmbedTitles.HELP, colour=nextcord.Colour.from_rgb(*Colours.SUCCESS))

        for command in commands:
            embed.add_field(name=command[0], value=command[1], inline=False)
        
        await ctx.send(content=None, embed=embed)

    async def send_gif(self, ctx: commands.Context, gif: Gif) -> None:
        '''Sends an embed representing a GIF.'''

        embed = (nextcord.Embed(colour=nextcord.Colour.from_rgb(*Colours.SUCCESS), title=gif.query, url=gif.gif_page)
                .set_footer(text='Via Tenor')
                .set_image(url=gif.url))

        await ctx.send(content=None, embed=embed)

    async def send_emote(self, ctx: commands.Context, emote: Emote) -> None:
        '''Sends an embed representing an emote.'''

        embed = (nextcord.Embed(colour=nextcord.Colour.from_rgb(*Colours.SUCCESS), title=emote.name)
                .set_image(url=emote.url))

        await ctx.send(content=None, embed=embed)


embed_sender_service = EmbedSenderService()
