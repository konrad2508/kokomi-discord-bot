from enum import Enum, auto


class EmoteProviders(Enum):
    '''Enum representing emote providers.'''

    SEVENTV = auto()

    def encode(self):
        '''Returns assigned value.'''

        return self.value
