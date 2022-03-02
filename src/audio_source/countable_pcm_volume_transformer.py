from nextcord import PCMVolumeTransformer


class CountablePCMVolumeTransformer(PCMVolumeTransformer):
    '''Class extending PCMVolumeTransformer to make it possible to get the current time of
    the song being played.'''

    def __init__(self, original, volume: float = 1.):
        super().__init__(original, volume)

        self._read_count = 0

    def read(self) -> bytes:
        self._read_count += 1

        return super().read()
    
    def current_time(self) -> int:
        '''Gets the current time of the song in seconds.'''
        
        # 1 read every 20ms => 50 reads every 1s
        return self._read_count // 50
