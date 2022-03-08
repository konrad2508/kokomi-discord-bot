from model.enum.emote_providers import EmoteProviders
from model.exception.no_provider_exception import NoProviderException
from model.reaction.emote import Emote
from service.seventv_service import SevenTvService, seven_tv_provider


class EmoteService:
    '''Class responsible for returning an emote object from an adequate provider.'''

    def __init__(self, seventv_provider: SevenTvService) -> None:
        self.seventv_provider = seventv_provider

    async def get_emote(self, query: str, provider: EmoteProviders) -> Emote:
        '''Gets an emote from provider based on query.'''

        match provider:
            case EmoteProviders.SEVENTV:
                gif = self.seventv_provider.get_emote(query)
 
            case _:
                raise NoProviderException

        return gif


emote_service = EmoteService(seven_tv_provider)
