import os

from dotenv import load_dotenv, find_dotenv


class Config:
    '''Class containing configuration for the program.'''

    def __init__(self) -> None:
        load_dotenv(find_dotenv())

        self.token = os.environ.get('BOT_TOKEN', '')
        self.prefix = os.environ.get('BOT_PREFIX', '')
        
        self.tenor_token = os.environ.get('TENOR_TOKEN', '')
        self.tenor_limit = os.environ.get('TENOR_LIMIT', '')


conf = Config()
