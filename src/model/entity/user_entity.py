from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserEntity:
    '''Entity representing an user.'''

    id: int

    def to_dict(self) -> dict:
        '''Returns a dict that can be stored in the database.'''

        entity_dict = self.__dict__

        return entity_dict
    
    @classmethod
    def from_dict(cls, dict: dict) -> UserEntity:
        '''Creates an instance of UserEntity based on a dictionary.'''

        return cls(
            id=dict['id']
        )
