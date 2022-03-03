from dataclasses import dataclass

from nextcord import VoiceClient

from audio_source.i_pcm_source import IPCMSource
from model.music.song import Song


@dataclass
class VC:
    '''Dataclass representing a connection to a voice channel.'''

    connection: VoiceClient
    is_queue_locked: bool
    queue: list[Song]
    currently_playing: IPCMSource | None
    currently_playing_song: Song | None
    is_looped: bool

    def is_queue_empty(self):
        '''Returns True if the music queue is empty, False otherwise.'''

        return len(self.queue) == 0
