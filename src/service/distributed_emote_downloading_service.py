import aiohttp
import logging
import uuid
from io import BytesIO

from PIL import Image

from config import Config, conf
from model.exception.emote_fetch_error import EmoteFetchError
from model.exception.unsupported_mime import UnsupportedMime
from service.i_emote_downloading_service import IEmoteDownloadingService


class DistributedEmoteDownloadingService(IEmoteDownloadingService):
    '''Class responsible for downloading an emote in suitable format. Might use a dedicated microservice for
    emote conversion.'''

    def __init__(self, config: Config) -> None:
        self.config = config

    async def download(self, emote_mime: str, emote_content: bytes) -> str:
        '''Downloads an emote from emote_content byte stream. emote_mime is used to determine
        whether conversion is needed (and how to convert). If a conversion
        is needed, uses an external microservice. Returns filename of downloaded emote.'''

        logging.info('downloading and converting an emote')

        emote_filename = uuid.uuid4().hex

        match emote_mime:
            case 'image/webp':
                emote_bytes = BytesIO(emote_content)
                
                em = Image.open(emote_bytes)
                emote_bytes.seek(0)

                if em.is_animated:
                    logging.info('emote is an animated webp')

                    async with aiohttp.ClientSession() as sess:
                        async with sess.post(
                            url=f'{self.config.emote_downloader_url}/animated/webp',
                            data=emote_content,
                            headers={'Content-Type': 'application/octet-stream'},
                            timeout=None
                        ) as r:
                            if r.status != 200:
                                logging.error(f'error fetching converted emote from microservice')
                                raise EmoteFetchError

                            converted_emote = await r.read()

                    emote_filename = f'{emote_filename}.gif'

                else:
                    logging.info('emote is a static webp')

                    async with aiohttp.ClientSession() as sess:
                        async with sess.post(
                            url=f'{self.config.emote_downloader_url}/static/webp',
                            data=emote_content,
                            headers={'Content-Type': 'application/octet-stream'},
                            timeout=None
                        ) as r:
                            if r.status != 200:
                                logging.error(f'error fetching converted emote from microservice')
                                raise EmoteFetchError

                            converted_emote = await r.read()

                    emote_filename = f'{emote_filename}.png'
                
                with open(emote_filename, 'wb') as f:
                    f.write(converted_emote)

            case 'image/gif':
                logging.info('emote is a gif')

                async with aiohttp.ClientSession() as sess:
                    async with sess.post(
                        url=f'{self.config.emote_downloader_url}/animated/gif',
                        data=emote_content,
                        headers={'Content-Type': 'application/octet-stream'},
                        timeout=None
                    ) as r:
                        if r.status != 200:
                            logging.error(f'error fetching converted emote from microservice')
                            raise EmoteFetchError

                        converted_emote = await r.read()

                emote_filename = f'{emote_filename}.gif'

                with open(emote_filename, 'wb') as f:
                    f.write(converted_emote)

            case 'image/png':
                logging.info('emote is a png')

                emote_filename = f'{emote_filename}.png'

                with open(emote_filename, 'wb') as f:
                    f.write(emote_content)

            case _:
                logging.error(f'unsupported mime: {emote_mime}')
                raise UnsupportedMime

        return emote_filename


emote_downloader = DistributedEmoteDownloadingService(conf)
