import json
import logging

import requests

from config import Config, conf
from model.exception.emote_fetch_error import EmoteFetchError
from model.exception.no_emote_results import NoEmoteResults
from model.reaction.emote import Emote


class SevenTvService:
    '''Class responsible for getting emotes from 7TV.'''

    def __init__(self, conf: Config) -> None:
        self.config = conf

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
            emotes_not_webp = [ emote for emote in emotes['data']['search_emotes'] if emote['mime'] not in ('image/webp', 'image/gif') ]
            
            emote = emotes_not_webp[0]
            emote_id = emote["id"]
            emote_name = emote['name']

            cdn_url = f'{self.config.seventv_emote_url}/{emote_id}/4x'

            return Emote(emote_name, cdn_url)

        except IndexError:
            logging.warning(f'could not find emote results for query "{query}"')

            raise NoEmoteResults


seven_tv_provider = SevenTvService(conf)
