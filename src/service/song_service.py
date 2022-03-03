import logging

from audio_source.ytdlp_pcm_source import YtdlpPCMSource
from model.music.song import Song


class SongService:
    '''Class responsible for returning a song object as an adequate class.'''

    async def get_song(self, source: str) -> Song:
        logging.info(f'getting song for {source}')

        song = await Song.create(YtdlpPCMSource, source)

        return song


song_service = SongService()
