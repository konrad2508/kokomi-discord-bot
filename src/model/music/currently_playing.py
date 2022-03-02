from dataclasses import dataclass

from model.music.duration import Duration


@dataclass
class CurrentlyPlaying:
    '''Dataclass containing information about the currently playing song.'''

    title: str
    url: str
    current_duration: Duration
    total_duration: Duration
