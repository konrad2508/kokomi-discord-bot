from dataclasses import dataclass

from model.reaction.emote import Emote


@dataclass
class OnlineEmote(Emote):
    '''Dataclass representing an emote stored online, accessed via an url.'''

    url: str
