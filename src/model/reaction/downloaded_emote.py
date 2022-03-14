from dataclasses import dataclass

from model.reaction.emote import Emote


@dataclass
class DownloadedEmote(Emote):
    '''Dataclass representing an emote downloaded and converted from the Internet, now stored locally as a file.'''

    filename: str
