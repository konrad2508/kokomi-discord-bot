from dataclasses import dataclass


@dataclass
class Gif:
    '''Dataclass representing a GIF'''

    query: str
    url: str
    gif_page: str
