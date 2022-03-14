import os

import nextcord
from nextcord.ext import commands

from colours import Colours
from embed_titles import EmbedTitles
from model.exception.too_large_emote import TooLargeEmote
from model.reaction.cached_emote import CachedEmote
from model.reaction.downloaded_emote import DownloadedEmote
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

    async def send_emote(self, ctx: commands.Context, emote: Emote) -> str:
        '''Sends an emote. Returns the url of the sent emote, to allow caching.'''

        match emote:
            case DownloadedEmote():
                try:
                    embed = (nextcord.Embed(colour=nextcord.Colour.from_rgb(*Colours.SUCCESS), title=emote.name)
                            .set_image(url=f'attachment://{emote.filename}'))

                    message = await ctx.send(content=None, embed=embed, file=nextcord.File(emote.filename))

                    return message.embeds[0].image.proxy_url

                except nextcord.HTTPException as e:
                    if e.status == 413:
                        raise TooLargeEmote

                    else:
                        raise

                finally:
                    os.remove(emote.filename)

            case CachedEmote():
                embed = (nextcord.Embed(colour=nextcord.Colour.from_rgb(*Colours.SUCCESS), title=emote.name)
                        .set_image(url=emote.url))
                
                await ctx.send(content=None, embed=embed)

                return emote.url

            case _:
                raise RuntimeError('emote should not be of type Emote, should be derived')


embed_sender_service = EmbedSenderService()
