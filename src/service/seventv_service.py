import json
import logging

import requests

from config import Config, conf
from model.exception.emote_fetch_error import EmoteFetchError
from model.exception.no_emote_results import NoEmoteResults
from model.reaction.emote import Emote
from service.emote_downloading_service import EmoteDownloadingService, emote_downloader
from service.i_emote_provider_service import IEmoteProviderService


class SeventvProviderService(IEmoteProviderService):
    '''Class responsible for getting emotes from 7TV.'''

    def __init__(self, conf: Config, emote_downloader: EmoteDownloadingService) -> None:
        self.config = conf
        self.emote_downloader = emote_downloader

    def get_emote(self, query: str) -> Emote:
        '''Gets an emote based on query from 7TV.'''

        r = requests.post(self.config.seventv_base_url, json={
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
                'query': query,
                'sortBy': 'popularity',
                'sortOrder': 0
            }
        })

        if r.status_code != 200:
            logging.error(f'status code of a request not 200 - is {r.status_code} for query "{query}"')

            raise EmoteFetchError
        
        try:
            emotes = json.loads(r.content)
            
            matching_emotes = [ emote for emote in emotes['data']['search_emotes'] if emote['name'].lower() == query.lower() ]
            all_emotes = emotes['data']['search_emotes']

            emote = matching_emotes[0] if len(matching_emotes) > 0 else all_emotes[0]

            emote_id = emote['id']
            emote_name = emote['name']
            emote_mime = emote['mime']

            cdn_url = f'{self.config.seventv_emote_url}/{emote_id}/4x'
            
            emote_content = requests.get(cdn_url).content
            emote_filename = self.emote_downloader.download(emote_mime, emote_content)
            
            return Emote(emote_name, emote_filename)

        except IndexError:
            logging.warning(f'could not find emote results for query "{query}"')

            raise NoEmoteResults


seven_tv_provider = SeventvProviderService(conf, emote_downloader)
