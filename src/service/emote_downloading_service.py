import asyncio
import logging
import uuid
from io import BytesIO

from PIL import Image

from model.exception.unsupported_mime import UnsupportedMime


class EmoteDownloadingService:
    '''Class responsible for downloading an emote in suitable format.'''

    async def download(self, emote_mime: str, emote_content: bytes) -> str:
        '''Downloads an emote from emote_content byte stream. emote_mime is used to determine
        whether conversion is needed (and how to convert). Returns filename of downloaded emote.'''

        emote_filename = uuid.uuid4().hex

        match emote_mime:
            case 'image/webp':
                emote_bytes = BytesIO(emote_content)
                
                em = Image.open(emote_bytes)
                emote_bytes.seek(0)

                if em.is_animated:
                    emote_filename = f'{emote_filename}.gif'

                    pipe = await asyncio.create_subprocess_exec('convert', '-', '-coalesce', emote_filename, stdin=asyncio.subprocess.PIPE)

                else:
                    emote_filename = f'{emote_filename}.png'

                    pipe = await asyncio.create_subprocess_exec('convert', '-', emote_filename, stdin=asyncio.subprocess.PIPE)
                
                await pipe.communicate(emote_bytes.read())

            case 'image/gif':
                emote_bytes = BytesIO(emote_content)

                emote_filename = f'{emote_filename}.gif'

                pipe = await asyncio.create_subprocess_exec('convert', '-', '-coalesce', emote_filename, stdin=asyncio.subprocess.PIPE)
                await pipe.communicate(emote_bytes.read())

            case 'image/png':
                emote_filename = f'{emote_filename}.png'

                with open(emote_filename, 'wb') as f:
                    f.write(emote_content)

            case _:
                logging.error(f'unsupported mime: {emote_mime}')
                raise UnsupportedMime

        return emote_filename


emote_downloader = EmoteDownloadingService()
