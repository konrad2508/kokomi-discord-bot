import logging
import re

from audio_source.ytdlp_pcm_source import YtdlpPCMSource
from model.exception.song_is_playlist import SongIsPlaylist
from model.music.song import Song


class SongService:
    '''Class responsible for returning a song object as an adequate class.'''

    async def get_song(self, source: str) -> Song:
        logging.info(f'getting song for {source}')

        if re.match(r'^.*www.youtube.com\/playlist', source) is not None:
            raise SongIsPlaylist
        else:
            song = await Song.create(YtdlpPCMSource, source)

        return song


song_service = SongService()
