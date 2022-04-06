from __future__ import annotations

import logging
import re
from typing import Type

import spotipy

from audio_source.ytdlp_pcm_source import YtdlpPCMSource


class SpotipyPCMSource(YtdlpPCMSource):
    @classmethod
    async def from_search(cls: Type[SpotipyPCMSource], url: str) -> SpotipyPCMSource:
        logging.info(f'getting song from spotify for {url}')
        
        if re.match(r'^.*open\.spotify\.com', url) is None:
            return await super().from_search(url)

        cm = spotipy.SpotifyClientCredentials()
        sp = spotipy.Spotify(client_credentials_manager=cm)

        track_meta = sp.track(url)

        track_name = track_meta['name']
        track_author = track_meta['artists'][0]['name']
        song = f'{track_author} - {track_name}'

        return await super().from_search(song)
