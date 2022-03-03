from __future__ import annotations

import logging
from typing import Type

import yt_dlp
from nextcord import FFmpegPCMAudio, AudioSource

from audio_source.i_pcm_source import IPCMSource


class YtdlpPCMSource(IPCMSource):
    '''Class representing a song found using yt-dlp library.'''

    _YTDL_FORMAT_OPTIONS = {
        'format': 'bestaudio/best',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto'
    }

    _FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    def __init__(self, source: AudioSource, data: dict, filename: str) -> None:
        super().__init__(source, volume=0.5)

        self.title: str = data.get('title', '')
        self.url: str = data.get('webpage_url', '')
        self.duration: int = int(data.get('duration', 0))

        self._filename = filename
        self._data = data

    @classmethod
    async def from_search(cls: Type[YtdlpPCMSource], url: str) -> YtdlpPCMSource:
        '''Performs a yt-dlp search for a song, based on search argument. Returns an instance representing the found song.

        In case of a url, represents the song behind that link. In case of a query,
        searches YouTube and represents the song behind the first search result.'''

        logging.info(f'fetching info for {url}')

        ytdl = yt_dlp.YoutubeDL(cls._YTDL_FORMAT_OPTIONS)
        data: dict = ytdl.extract_info(url, download=False)

        logging.info(f'found info for {url}')

        if 'entries' in data: 
            data = data['entries'][0]

        filename = data['url']

        return cls(FFmpegPCMAudio(filename, **cls._FFMPEG_OPTIONS), data, filename)

    async def get_new_instance(self) -> YtdlpPCMSource:
        logging.info(f'getting new instance of {self._filename}')

        new_instance = YtdlpPCMSource(FFmpegPCMAudio(self._filename, **self._FFMPEG_OPTIONS), self._data, self._filename)

        self.cleanup()

        return new_instance
