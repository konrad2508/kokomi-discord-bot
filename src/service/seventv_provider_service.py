import logging
import aiohttp

from config import Config, conf
from model.exception.emote_fetch_error import EmoteFetchError
from model.exception.no_emote_results import NoEmoteResults
from model.reaction.downloaded_emote import DownloadedEmote
from service.distributed_emote_downloading_service import emote_downloader
from service.i_emote_downloading_service import IEmoteDownloadingService
from service.i_emote_provider_service import IEmoteProviderService


class SeventvProviderService(IEmoteProviderService):
    '''Class responsible for getting emotes from 7TV.'''

    def __init__(self, conf: Config, emote_downloader: IEmoteDownloadingService) -> None:
        self.config = conf
        self.emote_downloader = emote_downloader

    async def get_emote(self, query: str, use_raw: bool) -> DownloadedEmote:
        '''Gets an emote based on query from 7TV.'''

        fixed_query = query.split(' ')[1] if use_raw else query

        logging.info(f'getting a 7tv emote for "{query}"')

        query_json = {
            'query': '''
                query(
                    $query: String!,
                    $page: Int,
                    $pageSize: Int,
                    $globalState: String,
                    $sortBy: String,
                    $sortOrder: Int,
                    $channel: String,
                    $submitted_by: String,
                    $filter: EmoteFilter) {
                        search_emotes(
                            query: $query,
                            limit: $pageSize,
                            page: $page,
                            pageSize: $pageSize,
                            globalState: $globalState,
                            sortBy: $sortBy,
                            sortOrder: $sortOrder,
                            channel: $channel,
                            submitted_by: $submitted_by,
                            filter: $filter) {
                                id,
                                visibility,
                                name,
                                mime
                            }
                    }
            ''',
            'variables': {
                'globalState': 'include',
                'pageSize': int(self.config.seventv_limit),
                'query': fixed_query,
                'sortBy': 'popularity',
                'sortOrder': 0
            }
        }

        async with aiohttp.ClientSession() as sess:
            async with sess.post(self.config.seventv_base_url, json=query_json) as r:
                if r.status != 200:
                    logging.error(f'status code of a request not 200 - is {r.status} for query "{query}"')
                    raise EmoteFetchError

                emotes = await r.json()

            try:
                all_emotes = emotes['data']['search_emotes']
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
                emote_mime = emote['mime']

                logging.info('found a 7tv emote')

                cdn_url = f'{self.config.seventv_emote_url}/{emote_id}/4x'

                async with sess.get(cdn_url) as r:
                    emote_content = await r.content.read()

                emote_filename = await self.emote_downloader.download(emote_mime, emote_content)
                logging.info(f'downloaded {emote_name}')

                return DownloadedEmote(emote_name, emote_filename)

            except IndexError:
                logging.warning(f'could not find emote results for query "{query}"')
                raise NoEmoteResults


seventv_provider = SeventvProviderService(conf, emote_downloader)
