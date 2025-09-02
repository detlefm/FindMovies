from datetime import datetime
import re
from openai import OpenAI, AsyncOpenAI
from openai.types.chat.chat_completion import ChatCompletion
from dotenv import load_dotenv
from os import getenv
import asyncio
from typing import Optional

load_dotenv()


class BaseChatClient:
    """Basisklasse mit gemeinsamen Funktionalitäten für sync und async Chatbots"""
    
    def __init__(self,  
                 provider:str,
                 base_url:str,                 
                 api_key:str= '',
                 model: Optional[str] = None,
                 ):
        
        self.default_model: Optional[str] = model 
        self.provider = provider
        self._base_url = base_url
        self._api_key = api_key
    
    def _get_headers(self) -> dict[str, str]:
        """Zusätzliche Header für die API-Anfrage"""
        return {
            "HTTP-Referer": "xyz.de",
            "X-Title": "FindMovies",
        }
    
    def info(self) -> dict:
        """Gibt Informationen über die Konfiguration zurück"""
        return {
            "provider": self.provider,
            "model": self.default_model,
            "base_url": str(self._base_url)
        } 
    
    @staticmethod
    def get_result_content(completion: ChatCompletion) -> str:
        """Extrahiert den Inhalt aus der Completion"""
        if (response_text := completion.choices[0].message.content if completion.choices else None): 
            # remove thinking, hack for ollama thinking models 
            return re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL).strip() 
        return ''


class ChatClient(BaseChatClient):
    """Synchrone Chatbot-Klasse"""
    
    def __init__(self,  
                 provider:str,
                 base_url:str,                 
                 api_key:str= '',
                 model: Optional[str] = None,
                 ):
        super().__init__(api_key=api_key, base_url=base_url, model=model, provider=provider)
        self.client: OpenAI = OpenAI(api_key=api_key, base_url=base_url)
    
    def ask(self, messages: list[dict[str, str]], model: Optional[str] = None) -> ChatCompletion:
        """Synchrone Anfrage"""
        model = model or self.default_model
        if not model:
            raise AttributeError('model not set')
        
        completion = self.client.chat.completions.create(
            model=model,
            extra_headers=self._get_headers(),
            messages=messages,  # type: ignore
        )
        return completion


class AsyncChatClient(BaseChatClient):
    """Asynchrone Chatbot-Klasse"""
    
    def __init__(self,  
                 provider:str,
                 base_url:str,                 
                 api_key:str= '',
                 model: Optional[str] = None,
                 ):
        super().__init__(api_key=api_key, base_url=base_url, model=model, provider=provider)
        self.client_async: AsyncOpenAI = AsyncOpenAI(api_key=api_key, base_url=base_url)
    
    async def ask(self, messages: list[dict[str, str]], model: Optional[str] = None) -> ChatCompletion:
        """Asynchrone Anfrage"""
        model = model or self.default_model
        if not model:
            raise AttributeError('model not set')
        
        completion = await self.client_async.chat.completions.create(
            model=model,
            extra_headers=self._get_headers(),
            messages=messages,  # type: ignore
        )
        return completion