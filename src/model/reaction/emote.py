from dataclasses import dataclass


@dataclass
class Emote:
    '''Dataclass serving as a base class for emotes. Should not be instantiated.'''

    name: str
