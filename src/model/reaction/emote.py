from dataclasses import dataclass


@dataclass
class Emote:
    '''Dataclass representing an emote'''

    name: str
    filename: str
