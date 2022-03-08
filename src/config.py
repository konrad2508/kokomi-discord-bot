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


conf = Config()
