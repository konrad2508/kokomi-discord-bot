from __future__ import annotations

from dataclasses import dataclass

from model.enum.emote_providers import EmoteProviders


@dataclass
class EmoteEntity:
    '''Entity representing an emote.'''

    name: str
    query: str
    provider: EmoteProviders
    url: str

    def to_dict(self) -> dict:
        '''Returns a dict that can be stored in the database.'''

        entity_dict = self.__dict__

        entity_dict['provider'] = entity_dict['provider'].encode()

        return entity_dict
    
    @classmethod
    def from_dict(cls, dict: dict) -> EmoteEntity:
        '''Creates an instance of EmoteEntity based on a dictionary.'''

        return cls(
            name=dict['name'],
            query=dict['query'],
            provider=dict['provider'],
            url=dict['url']
        )
