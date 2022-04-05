from model.enum.emote_providers import EmoteProviders
from model.exception.no_provider_exception import NoProviderException
from model.reaction.downloaded_emote import DownloadedEmote
from service.i_emote_provider_service import IEmoteProviderService
from service.bttv_provider_service import bttv_provider
from service.seventv_provider_service import seventv_provider


class EmoteService:
    '''Class responsible for returning an emote object from an adequate provider.'''

    def __init__(self, providers: dict[EmoteProviders, IEmoteProviderService]) -> None:
        self.providers = providers

    async def get_emote(self, query: str, provider: EmoteProviders, use_raw: bool) -> DownloadedEmote:
        '''Gets an emote from provider based on query.'''

        try:
            provider_service = self.providers[provider]
        
        except KeyError:
            raise NoProviderException

        gif = await provider_service.get_emote(query, use_raw)

        return gif


emote_service = EmoteService({
    EmoteProviders.SEVENTV: seventv_provider,
    EmoteProviders.BTTV: bttv_provider
})
