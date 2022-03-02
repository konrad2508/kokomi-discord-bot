import textwrap

from audio_source.i_pcm_source import IPCMSource
from model.music.currently_playing import CurrentlyPlaying


class Messages:
    '''Class containing messages sent in various types of embeds.'''

    AUTHOR_NOT_IN_SERVER = 'Command unavailable through DM'
    AUTHOR_NOT_IN_VOICE_CHAT = 'You must be in a voice channel'
    BOT_ALREADY_IN_VOICE_CHAT = 'Bot is already in a voice channel'
    BOT_NOT_IN_VOICE_CHAT = 'Bot is not in a voice channel'
    BOT_JOINED_VOICE_CHAT = 'Joined voice channel'
    BOT_LEFT_VOICE_CHAT = 'Left voice channel'
    MUSIC_QUEUE_IS_LOCKED = 'The queue is locked'
    NO_SONG_PLAYING = 'No song is currently playing'
    LOOPING_SONG = 'Looping currently playing song'
    UNLOOPING_SONG = 'Unlooping currently playing song'
    MISSING_ARGUMENTS = 'Provide argument(s) to the command'
    QUEUE_ENDED = 'Queue ended'
    EMPTY_QUEUE = 'The queue is empty'
    SKIPPED_SONG = 'Skipped currently playing song'
    ERROR_FETCHING_GIFS = 'There was an error fetching GIFs'

    @staticmethod
    def CURRENTLY_PLAYING(currently_playing: CurrentlyPlaying) -> str:
        tot_dur = currently_playing.total_duration
        curr_dur = currently_playing.current_duration
        
        msg = f'''\
            Currently playing: [{currently_playing.title}]({currently_playing.url})
            Current time: {curr_dur.as_timestamp(force_hours=tot_dur.has_hours())}/{tot_dur.as_timestamp()}
            '''

        return textwrap.dedent(msg)

    @staticmethod
    def ADDED_SONG(title: str, url: str) -> str:
        return f'Added [{title}]({url}) to the queue'
    
    @staticmethod
    def PLAYING_SONG(title: str, url: str) -> str:
        return f'Playing [{title}]({url})'

    @staticmethod
    def SONG_QUEUE(currently_playing: IPCMSource, queue: list[IPCMSource], is_looped: bool) -> str:
        nl = '\n'
        looped_str = f' (looped)' if is_looped else ''
        queue_str = f"{nl}{nl.join([ f'{i}. [{song.title}]({song.url})' for i, song in enumerate(queue, 2) ])}" if len(queue) > 0 else ''
        msg = f'''\
            Queue:
            1. [{currently_playing.title}]({currently_playing.url}) (currently playing){looped_str}{queue_str}
            '''
        
        return msg

    @staticmethod
    def NO_GIFS_FOUND(query: str) -> str:
        return f'Could not find a GIF for "{query}"'
    
    @staticmethod
    def HELP(prefix: str) -> list[tuple[str, str]]:
        commands = [
            (f"```{prefix}help```", "Displays this message"),
            (f"```{prefix}join```", "Joins your voice channel"),
            (f"```{prefix}leave```", "Leaves the voice channel"),
            (f"```{prefix}loop```", "Loops (or unloops) currently playing song"),
            (f"```{prefix}nowplaying```", "Shows information about the currently playing song"),
            (f"```{prefix}play <URL | Query>```", "Plays a song from **URL** or plays the first song from YouTube based on **Query**"),
            (f"```{prefix}queue```", "Shows the song queue"),
            (f"```{prefix}skip```", "Skips the currently playing song")
        ]

        return commands
