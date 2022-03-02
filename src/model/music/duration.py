from dataclasses import dataclass


@dataclass
class Duration:
    '''Dataclass representing the time of the song in seconds.'''

    sec: int

    def as_timestamp(self, force_hours: bool = False) -> str:
        '''Returns duration as HH:MM:SS if force_hours or there is at least an hour,
        else MM:SS.'''

        minutes = self.sec // 60
        hours = minutes // 60

        display_minutes = minutes % 60
        display_sec = self.sec % 60

        if force_hours or hours > 0:
            return f'{hours:02d}:{display_minutes:02d}:{display_sec:02d}'
        
        else:
            return f'{display_minutes:02d}:{display_sec:02d}'
    
    def has_hours(self) -> bool:
        '''Checks if there is at least an hour.'''

        return self.sec // 3600 > 0
