import logging
import aiohttp

from config import Config, conf
from model.exception.emote_fetch_error import EmoteFetchError
from model.exception.no_emote_results import NoEmoteResults
from model.reaction.online_emote import OnlineEmote
from service.distributed_emote_downloading_service import emote_downloader
from service.i_emote_downloading_service import IEmoteDownloadingService
from service.i_emote_provider_service import IEmoteProviderService


class SeventvProviderService(IEmoteProviderService):
    '''Class responsible for getting emotes from 7TV.'''

    def __init__(self, conf: Config, emote_downloader: IEmoteDownloadingService) -> None:
        self.config = conf
        self.emote_downloader = emote_downloader

    async def get_emote(self, query: str, use_raw: bool) -> OnlineEmote:
        '''Gets an emote based on query from 7TV.'''

        fixed_query = query.split(' ')[1] if use_raw else query

        logging.info(f'getting a 7tv emote for "{query}"')

        query_json = {
            'query': '''
                query SearchEmotes(
                    $query: String!,
                    $page: Int,
                    $sort: Sort,
                    $limit: Int,
                    $filter: EmoteSearchFilter) {
                        emotes(
                            query: $query,
                            limit: $limit,
                            page: $page,
                            filter: $filter,
                            sort: $sort) {
                                items {
                                    id
                                    name
                                }
                            }
                    }
            ''',
            'variables': {
                'limit': int(self.config.seventv_limit),
                'query': fixed_query,
                'page': 1,
                'sort': {
                    'value': 'popularity',
                    'order': 'DESCENDING'
                },
                'filter': {
                    'category': 'TOP',
                    'exact_match': False,
                    'case_sensitive': False,
                    'ignore_tags': False,
                    'zero_width': False,
                    'animated': False,
                    'aspect_ratio': ''
                }
            }
        }

        async with aiohttp.ClientSession() as sess:
            async with sess.post(self.config.seventv_base_url, json=query_json) as r:
                if r.status != 200:
                    logging.error(f'status code of a request not 200 - is {r.status} for query "{query}"')
                    raise EmoteFetchError

                emotes = await r.json()

            try:
                all_emotes = emotes['data']['emotes']['items']
                exact_match_emotes = [ emote for emote in all_emotes if emote['name'] == fixed_query ]

                if use_raw:
                    emote = exact_match_emotes[0]

                else:
                    if fixed_query.islower():
                        emote = all_emotes[0]

                    else:
                        match_emotes = [ emote for emote in all_emotes if emote['name'].lower() == fixed_query.lower() ]

                        emote = exact_match_emotes[0] if len(exact_match_emotes) > 0 else match_emotes[0] if len(match_emotes) > 0 else all_emotes[0]

                emote_id = emote['id']
                emote_name = emote['name']

                logging.info('found a 7tv emote')

                cdn_url = f'{self.config.seventv_emote_url}/{emote_id}/4x'

                async with sess.head(f'{cdn_url}.gif') as r:
                    cdn_url = f'{cdn_url}.gif' if r.status == 200 else f'{cdn_url}.webp'

                logging.info(f'emote link seems to be {cdn_url}')

                return OnlineEmote(emote_name, cdn_url)

            except IndexError:
                logging.warning(f'could not find emote results for query "{query}"')
                raise NoEmoteResults


seventv_provider = SeventvProviderService(conf, emote_downloader)
