import logging
import aiohttp

from config import Config
from model.exception.emote_fetch_error import EmoteFetchError
from model.exception.no_emote_results import NoEmoteResults
from model.reaction.online_emote import OnlineEmote
from service.emote_downloading_service import EmoteDownloadingService
from service.i_emote_provider_service import IEmoteProviderService


class BttvProviderService(IEmoteProviderService):
    '''Class responsible for getting emotes from BTTV.'''

    def __init__(self, conf: Config, emote_downloader: EmoteDownloadingService) -> None:
        self.config = conf
        self.emote_downloader = emote_downloader

    async def get_emote(self, query: str, use_raw: bool) -> OnlineEmote:
        '''Gets an emote based on query from BTTV.'''

        fixed_query = query.split(' ')[1] if use_raw else query

        logging.info(f'getting a bttv emote for "{query}"')

        query_url = f'{self.config.bttv_base_url}/search?query={fixed_query}&limit={self.config.bttv_limit}'

        async with aiohttp.ClientSession() as sess:
            async with sess.get(query_url) as r:
                if r.status != 200:
                    logging.error(f'status code of a request not 200 - is {r.status} for query "{query}"')
                    raise EmoteFetchError

                emotes = await r.json()

            try:
                exact_match_emotes = [ emote for emote in emotes if emote['code'] == fixed_query ]

                if use_raw:
                    emote = exact_match_emotes[0]

                else:
                    if fixed_query.islower():
                        emote = emotes[0]

                    else:
                        match_emotes = [ emote for emote in emotes if emote['code'].lower() == fixed_query.lower() ]

                        emote = exact_match_emotes[0] if len(exact_match_emotes) > 0 else match_emotes[0] if len(match_emotes) > 0 else emotes[0]

                emote_id = emote['id']
                emote_name = emote['code']
                emote_type = emote['imageType']

                logging.info('found a bttv emote')

                cdn_url = f'{self.config.bttv_emote_url}/emote/{emote_id}/3x.{emote_type}'

                logging.info(f'emote link seems to be {cdn_url}')

                return OnlineEmote(emote_name, cdn_url)

            except IndexError:
                logging.warning(f'could not find emote results for query "{query}"')
                raise NoEmoteResults
