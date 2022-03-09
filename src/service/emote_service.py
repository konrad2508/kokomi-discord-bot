from model.enum.emote_providers import EmoteProviders
from model.exception.no_provider_exception import NoProviderException
from model.reaction.emote import Emote
from service.i_emote_provider_service import IEmoteProviderService
from service.seventv_service import seven_tv_provider


class EmoteService:
    '''Class responsible for returning an emote object from an adequate provider.'''

    def __init__(self, providers: dict[EmoteProviders, IEmoteProviderService]) -> None:
        self.providers = providers

    async def get_emote(self, query: str, provider: EmoteProviders) -> Emote:
        '''Gets an emote from provider based on query.'''

        try:
            provider_service = self.providers[provider]
        
        except KeyError:
            raise NoProviderException

        gif = await provider_service.get_emote(query)

        return gif


emote_service = EmoteService({
    EmoteProviders.SEVENTV: seven_tv_provider
})
