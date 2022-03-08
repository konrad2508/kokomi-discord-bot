import json
import logging
import random

import requests

from config import Config, conf
from model.exception.gif_fetch_error import GifFetchError
from model.exception.no_gif_results import NoGifResults
from model.reaction.gif import Gif


class GifService:
    '''Class responsible for fetching GIFs.'''

    def __init__(self, config: Config) -> None:
        self.config = config

    async def get_random_gif(self, query: str) -> Gif:
        '''Fetches a random GIF from Tenor based on query.'''

        logging.info(f'getting a gif for "{query}"')

        r = requests.get(
            f'{self.config.tenor_base_url}/search?q={query}&key={self.config.tenor_token}&limit={self.config.tenor_limit}'
        )

        if r.status_code != 200:
            logging.error(f'status code of a request not 200 - is {r.status_code} for query "{query}"')

            raise GifFetchError

        try:
            gifs = json.loads(r.content)

            selected_gif = random.choice(gifs['results'])

            gif_object = Gif(
                query,
                selected_gif['media'][0]['gif']['url'],
                selected_gif['url']
            )

            return gif_object

        except IndexError:
            logging.warning(f'could not find gif results for query "{query}"')

            raise NoGifResults


gif_service = GifService(conf)
