from __future__ import annotations

import os
import logging
from typing import Type

import yt_dlp
from nextcord import FFmpegPCMAudio, AudioSource

from audio_source.i_pcm_source import IPCMSource
from model.exception.source_authorization_error import SourceAuthorizationError
from model.exception.unsupported_source import UnsupportedSource


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
        'quiet': False,
        'verbose': True,
        'no_warnings': True,
        'default_search': 'auto',
        'force_ipv4': True,
        'extractor_args': {
            'youtube': {
                'player_client': ['mweb']
            }
        },
        'js_runtimes': {
            'node': { }
        },
        'remote_components': ['ejs:github']
    }

    _FFMPEG_OPTIONS = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        'options': '-vn'
    }

    def __init__(self, source: AudioSource, data: dict, filename: str, volume: float = .5) -> None:
        super().__init__(source, volume=volume)

        self.title: str = data.get('title', '')
        self.url: str = data.get('webpage_url', '')
        self.duration: int = int(float(data.get('duration', 0)))

        self._filename = filename
        self._data = data

    @classmethod
    async def from_search(cls: Type[YtdlpPCMSource], url: str, cookies: str = '') -> YtdlpPCMSource:
        '''Performs a yt-dlp search for a song, based on search argument. Returns an instance representing the found song.

        In case of a url, represents the song behind that link. In case of a query,
        searches YouTube and represents the song behind the first search result.'''

        logging.info(f'fetching info for {url}')

        try:
            ytdl_opts = cls._YTDL_FORMAT_OPTIONS

            if cookies != '':
                ytdl_opts['cookiefile'] = cookies

                logging.info(f'file exists: {os.path.exists(cookies)}')
                if os.path.exists(cookies):
                    logging.info(f'file size: {os.path.getsize(cookies)}')
                    with open(cookies, 'r') as f:
                        logging.info(f'first line: {repr(f.readline())}')


            ytdl = yt_dlp.YoutubeDL(ytdl_opts)
            data: dict = ytdl.extract_info(url, download=False)

        except yt_dlp.utils.DownloadError as e:
            if "Sign in to confirm you\u2019re not a bot." in str(e):
                raise SourceAuthorizationError

            else:
                raise UnsupportedSource

        logging.info(f'found info for {url}')

        if 'entries' in data: 
            data = data['entries'][0]

        filename = data['url']

        ffmpeg_options = cls._FFMPEG_OPTIONS
        headers = ''.join(f'{k}: {v}\r\n' for k, v in data.get('http_headers', {}).items())
        user_agent = data.get('http_headers', {}).get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)')
        ffmpeg_options['before_options'] = f'{ffmpeg_options['before_options']} -headers "{headers}" -user_agent "{user_agent}"'

        return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data, filename)
