from config import Config
from model.enum.emote_providers import EmoteProviders
from repository.mongo_database_repository import MongoDatabaseRepository
from service.bttv_provider_service import BttvProviderService
from service.convertor_service import ConvertorService
from service.database_service import DatabaseService
from service.distributed_emote_downloading_service import DistributedEmoteDownloadingService
from service.embed_sender_service import EmbedSenderService
from service.emote_downloading_service import EmoteDownloadingService
from service.emote_service import EmoteService
from service.gif_service import GifService
from service.markov_service import MarkovService
from service.music_player_service import MusicPlayerService
from service.seventv_provider_service import SeventvProviderService
from service.song_service import SongService
from service.user_management_service import UserManagementService


conf = Config()
convertor_service = ConvertorService()
embed_sender_service = EmbedSenderService()
emote_downloader = EmoteDownloadingService()
markov_service = MarkovService()
song_service = SongService()
mongo_database_repository = MongoDatabaseRepository(conf)
emote_downloader = DistributedEmoteDownloadingService(conf)
gif_service = GifService(conf)
music_player_service = MusicPlayerService(song_service)
bttv_provider = BttvProviderService(conf, emote_downloader)
seventv_provider = SeventvProviderService(conf, emote_downloader)
database_service = DatabaseService(mongo_database_repository, convertor_service)
user_management_service = UserManagementService(conf, database_service)
emote_service = EmoteService({
    EmoteProviders.SEVENTV: seventv_provider,
    EmoteProviders.BTTV: bttv_provider
})
