# pip install pydantic-settings python-dotenv
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import yaml
from dotenv import load_dotenv
load_dotenv()

class AiProviderData(BaseModel):
    models: set[str]
    ep: str  # endpoint

    @field_validator("models", mode="before")
    @classmethod
    def _split_models(cls, value):
        """
        Nimmt einen Komma-String und macht daraus ein Set[str].
        Leere Einträge und Whitespace werden ignoriert.
        """
        if isinstance(value, str):
            return {part.strip() for part in value.split(",") if part.strip()}
        return value  # bereits eine Collection → unverändert lassen

class Settings(BaseSettings):
    server_url: str = 'http://localhost:8089'
    data_folder: str = './data'
    plugin_folder: str = './plugins'
    log_folder: str = './data'
    epg_filter: Dict[str, Any] = {}
    timerparameters: Dict[str, int] = {'pre': 5, 'post': 5}
    ai_model: Optional[str] = None
    ai_provider: Dict[str, AiProviderData] = {}

    model_config = SettingsConfigDict(
        # env_file=".env",        # lädt zusätzlich Variablen aus .env
        # env_file_encoding="utf-8",
        case_sensitive=False
    )

settings: Settings = None  # type: ignore

def init_config(filename: str = './app.yaml'):
    global settings
    with open(file=filename, mode='r', encoding='utf-8') as f:
        settings = Settings(**yaml.safe_load(f))
    return settings