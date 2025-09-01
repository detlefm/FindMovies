from __future__ import annotations
from contextlib import asynccontextmanager, contextmanager
import os
from typing import Optional
from .services.chat_service import AsyncChatClient, ChatClient
from . import config as cfg
import httpx
from typing import AsyncGenerator, Generator

from .services.ms_service import AsyncMediaServer
from .services.ms_service import MediaServer
from .mediasrv_ctrl import MS_ControllerBase, AsyncMS_Controller, MS_Controller
from .services.ms_service import AbstractMediaServer


_chat_client = None


def chat_client_data(
        settings:cfg.Settings,
        model:Optional[str]=None,
        api_key:Optional[str]=None
        ) -> dict:

    ai_model = model or settings.ai_model
    # if no model set we can't chat
    if not ai_model:
        raise ValueError('No model set')
    # we need at least one provider
    if not settings.ai_provider:
        raise ValueError('No provider found')
    # find provider
    provider = ''
    for key, providerdata in settings.ai_provider.items():
        if settings.ai_model in providerdata.models:
            provider = key
            break
    if not provider:
        raise ValueError(f'No provider found for model {settings.ai_model}')
    api_key = api_key or os.getenv(f'{provider}_API_KEY'.upper(),'')
    if not api_key:
        raise ValueError(f'No API key found for provider {provider}')  
     
    return {'api_key':api_key,
            'base_url':settings.ai_provider[provider].ep,
            'model':settings.ai_model,
            'provider':provider}



def chat_client(
        settings:cfg.Settings,
        model:Optional[str]=None,
        api_key:Optional[str]=None
        ) -> ChatClient:
    
    global _chat_client

    if _chat_client:
        return _chat_client

    ai_model = model or settings.ai_model
    # if no model set we can't chat
    if not ai_model:
        raise ValueError('No model set')
    # we need at least one provider
    if not settings.ai_provider:
        raise ValueError('No provider found')
    # find provider
    provider = ''
    for key, providerdata in settings.ai_provider.items():
        if settings.ai_model in providerdata.models:
            provider = key
            break
    if not provider:
        raise ValueError(f'No provider found for model {settings.ai_model}')
    api_key = api_key or os.getenv(f'{provider}_API_KEY'.upper(),'')
    if not api_key:
        raise ValueError(f'No API key found for provider {provider}')   
    _chat_client = ChatClient(api_key=api_key,base_url=settings.ai_provider[provider].ep,
                       model=settings.ai_model,provider=provider)
    return _chat_client


def create_sync_chat_client( 
        settings:cfg.Settings,
        model:Optional[str]=None,
        api_key:Optional[str]=None) -> ChatClient:
    """
    Erzeugt einen synchronen ChatClient
    """    
    client_data = chat_client_data(settings=settings,model=model,api_key=api_key)
    return ChatClient(
            api_key=client_data['api_key'],
            base_url=client_data['base_url'],
            model=client_data['model'],
            provider=client_data['provider'])


def create_async_chat_client( 
        settings:cfg.Settings,
        model:Optional[str]=None,
        api_key:Optional[str]=None) ->AsyncChatClient:
    """
    Erzeugt einen synchronen ChatClient
    """    
    client_data = chat_client_data(settings=settings,model=model,api_key=api_key)
    return  AsyncChatClient(**client_data) 



# ---------- Factory für FastAPI (synchron) ----------
@contextmanager
def create_sync_controller(base_url: str, debug: bool = False) -> Generator[MS_Controller, None, None]:
    """
    Erzeugt einen synchronen Controller mit eigenem httpx.Client.
    """    
    with httpx.Client() as client:
        media = MediaServer(client, base_url, debug=debug)
        yield MS_Controller(media)


# ---------- Factory für FastAPI (asynchron) ----------
@asynccontextmanager
async def create_async_controller(base_url: str, debug: bool = False) -> AsyncGenerator[AsyncMS_Controller, None]:
    """
    Erzeugt einen asynchronen Controller mit eigenem httpx.AsyncClient.
    """
    async with httpx.AsyncClient() as client:
        media = AsyncMediaServer(client, base_url, debug=debug)
        yield AsyncMS_Controller(media)