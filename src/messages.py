import textwrap

from audio_source.i_pcm_source import IPCMSource
from model.music.currently_playing import CurrentlyPlaying


class Messages:
    '''Class containing messages sent in various types of embeds.'''

    AUTHOR_NOT_IN_SERVER = 'Command unavailable through DM'
    AUTHOR_IN_SERVER = 'Command available through DM'
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
    ERROR_FETCHING_EMOTES = 'There was an error fetching an emote'
    EMOTE_TOO_LARGE = 'Requested emote is too large'
    UNSUPPORTED_SONG_SOURCE = 'Could not play the song from the specified website'
    INVALID_OPTION = 'Passed an invalid option to the command'
    SONG_IS_PLAYLIST = 'Specified link leads to a playlist'
    PLAYLIST_IS_SONG = 'Specified link leads to a song'
    UNSUPPORTED_PLAYLIST_SOURCE = 'Specified link leads to an unsupported source'
    CANNOT_ADD_PLAYLIST = 'Could not add the playlist to the queue'
    PURGED_QUEUE = 'The queue has been emptied'
    QUERY_TOO_LONG = 'The query is too long (must be 256 or fewer in length)'
    MARKOV_BAD_ARGUMENT = 'Specified argument is not a valid (or visible) text channel'
    MARKOV_NO_NEW_MESSAGES = 'No messages available for learning in the specified channel'
    MARKOV_CHANNEL_NOT_LEARNED = 'The bot must learn from the specified channel first'
    MARKOV_NOT_ENOUGH_DATA = 'The bot has not gained enough knowledge from the channel to be able to generate a message'
    USER_NOT_BANNABLE = 'User cannot be banned'
    USER_NOT_BANNED = 'Specified user is not banned'
    USER_BANNED = 'Specified user is already banned'
    USER_NOT_AUTHORIZED = 'Specified user is not authorized'
    USER_AUTHORIZED = 'Specified user is already authorized'
    MISSING_USER_ID = 'Provide ID of the user'
    USER_SUCCESSFULLY_UNBANNED = 'Successfully unbanned the user'
    USER_SUCCESSFULLY_UNAUTHORIZED = 'Successfully unauthorized the user'
    USER_SUCCESSFULLY_BANNED = 'Successfully banned the user'
    USER_SUCCESSFULLY_AUTHORIZED = 'Successfully authorized the user'


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
    def ADDED_PLAYLIST(count: int) -> str:
        return f"Added {count} song{'s' if count > 1 else ''}"

    @staticmethod
    def PLAYING_SONG(title: str, url: str) -> str:
        return f'Playing [{title}]({url})'

    @staticmethod
    def SONG_QUEUE(currently_playing: IPCMSource, queue: list[IPCMSource], is_looped: bool) -> str:
        QUEUE_SONG_LIMIT = 4

        sent_queue = queue[:QUEUE_SONG_LIMIT]
        rest_queue = queue[QUEUE_SONG_LIMIT:]
        
        nl = '\n'
        looped_str = f' (looped)' if is_looped else ''
        queue_str = f"{nl}{nl.join([ f'{i}. [{song.title}]({song.url})' for i, song in enumerate(sent_queue, 2) ])}" if len(sent_queue) > 0 else ''
        rest_str = f"{nl}And {len(rest_queue)} other song{'s' if len(rest_queue) > 1 else ''}" if len(rest_queue) > 0 else ''
        msg = f'''\
            Queue:
            1. [{currently_playing.title}]({currently_playing.url}) (currently playing){looped_str}{queue_str}{rest_str}
            '''
        
        return msg

    @staticmethod
    def NO_GIFS_FOUND(query: str) -> str:
        return f'Could not find a GIF for "{query}"'

    @staticmethod
    def NO_EMOTES_FOUND(query: str) -> str:
        return f'Could not find an emote for "{query}"'
    
    @staticmethod
    def FINISHED_LEARNING(number_of_messages: int) -> str:
        return f'Finished learning from {number_of_messages} message(s)'

    @staticmethod
    def LIST_BANNED_USERS(banned_users: list[int]) -> str:
        if len(banned_users) == 0:
            return 'No banned users'

        else:
            return ', '.join(map(str, banned_users))

    @staticmethod
    def LIST_AUTHORIZED_USERS(authorized_users: list[int]) -> str:
        if len(authorized_users) == 0:
            return 'No authorized users'

        else:
            return ', '.join(map(str, authorized_users))

    @staticmethod
    def HELP(prefix: str) -> list[tuple[str, str]]:
        commands = [
            (f"```{prefix}help```", "Displays this message."),
            (f"```{prefix}join```", "Joins your voice channel."),
            (f"```{prefix}leave```", "Leaves the voice channel."),
            (f"```{prefix}loop```", "Loops (or unloops) the currently playing song."),
            (f"```{prefix}nowplaying```", "Shows information about the currently playing song."),
            (f"```{prefix}play [Option] <URL | Query>```", "Plays a song from **URL** or plays the first song from YouTube based on **Query**. If the option **--playlist** is passed, adds songs from the playlist in **URL** to the queue."),
            (f"```{prefix}queue```", "Shows the song queue."),
            (f"```{prefix}skip```", "Skips the currently playing song."),
            (f"```{prefix}purge```", "Clears the queue and stops the currently playing song."),
            (f"```{prefix}gif <Query>```", "Posts a random GIF from Tenor based on **Query**."),
            (f"```{prefix}7tv [Option] <Query>```", "Posts an emote from 7TV based on **Query**. If option **--raw** is passed, **Query** is interpreted as-is (the emote's name matches it exactly). Otherwise, an emote is selected based on the most probable intention of the author."),
            (f"```{prefix}bttv [Option] <Query>```", "Posts an emote from BTTV based on **Query**. If option **--raw** is passed, **Query** is interpreted as-is (the emote's name matches it exactly). Otherwise, an emote is selected based on the most probable intention of the author."),
            (f"```{prefix}learn <TextChannel>```", "Learns from messages sent in **TextChannel** to generate new, random messages. **TextChannel** must be a mention of the specified text channel."),
            (f"```{prefix}say <TextChannel>```", "Generates a random message based on messages sent in **TextChannel**. **Learn** command must be used on **TextChannel** first. **TextChannel** must be a mention of the specified text channel.")
        ]

        return commands
