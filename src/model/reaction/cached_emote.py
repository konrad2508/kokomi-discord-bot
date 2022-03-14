from dataclasses import dataclass

from model.reaction.emote import Emote


@dataclass
class CachedEmote(Emote):
    '''Dataclass representing an emote cached in the database, now accessed via an url.'''

    url: str
