import os

from dotenv import load_dotenv, find_dotenv


class Config:
    '''Class containing configuration for the program.'''

    def __init__(self) -> None:
        load_dotenv(find_dotenv())

        self.token = os.environ.get('BOT_TOKEN', '')
        self.prefix = os.environ.get('BOT_PREFIX', '')
        
        self.tenor_base_url = os.environ.get('TENOR_BASE_URL', '')
        self.tenor_token = os.environ.get('TENOR_TOKEN', '')
        self.tenor_limit = os.environ.get('TENOR_LIMIT', '')

        self.seventv_base_url = os.environ.get('SEVENTV_BASE_URL', '')
        self.seventv_emote_url = os.environ.get('SEVENTV_EMOTE_URL', '')
        self.seventv_limit = os.environ.get('SEVENTV_LIMIT', '')

        self.bttv_base_url = os.environ.get('BTTV_BASE_URL', '')
        self.bttv_emote_url = os.environ.get('BTTV_EMOTE_URL', '')
        self.bttv_limit = os.environ.get('BTTV_LIMIT', '')

        self.spotipy_client_id = os.environ.get('SPOTIPY_CLIENT_ID', '')
        self.spotipy_client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET', '')

        self.database_connection_string = os.environ.get('DATABASE_CONNECTION_STRING', '')
        self.database_name = os.environ.get('DATABASE_NAME', '')
        self.database_emote_collection_name = os.environ.get('DATABASE_EMOTE_COLLECTION_NAME', '')

        self.emote_downloader_url = os.environ.get('EMOTE_DOWNLOADER_URL', '')


conf = Config()
