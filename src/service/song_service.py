import logging

from audio_source.i_pcm_source import IPCMSource
from audio_source.ytdlp_pcm_source import YtdlpPCMSource


class SongService:
    '''Class responsible for returning a song object as an adequate class.'''

    async def get_song(self, source: str) -> IPCMSource:
        logging.info(f'getting song for {source}')

        return await YtdlpPCMSource.from_search(source)


song_service = SongService()
