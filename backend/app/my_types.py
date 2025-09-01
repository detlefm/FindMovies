from abc import ABC, abstractmethod
from datetime import datetime
from datetime import date
import hashlib
import re
from typing import List, Optional
from pydantic import BaseModel, Field, computed_field
from .services.tmdb_types import Tmdb_Movie, TVSerial



class EPG (BaseModel):
    eventid: int
    content: int = Field(default=0, exclude=False)
    pdc:int = Field(default=0)
    charset: int
    title: str
    event: str
    description: str
    start: datetime
    stop: datetime
    epgchannel: str    
    tv_channel:str =''
    tv_name:str = ''
    contentinfo:list[str] = Field(default_factory=list)

    @property
    def ismovie(self) -> bool:
        joined = ','.join(self.contentinfo).lower()
        if 'movie' in joined:
            return True
        return False
    

    @computed_field(return_type=str)  # Expliziter Typ für bessere Serialisierung
    @property
    def hash(self) -> str:
        """Calculates a hash based on the EPG content."""
        info = '|'.join(map(str, self.contentinfo))
        txt = self.title.strip() + self.description.strip() + info.strip() + self.event.strip()
        txt = re.sub(r'\[PDC.*?\]', '', txt).strip()
        txt = txt.lower().replace(' ', '')
        return hashlib.md5(txt.encode("utf-8")).hexdigest()
    
    @property
    def real_id(self) -> str:
        return f'{self.epgchannel}|{self.eventid}'
    
    @property
    def duration(self) -> int:
        return int((self.stop - self.start).total_seconds() / 60)

    
    def model_dump(self, **kwargs) -> dict:
        kwargs.setdefault('exclude_unset', True)  # Nur gesetzte Felder ausgeben
        data = super().model_dump(**kwargs)
        if self.pdc == 0:
            data.pop("pdc", None)
        return data
    


class EPGFilter(ABC):
    @abstractmethod
    def __call__(self, epg:EPG):
        pass

    @abstractmethod
    def __str__(self):
        return self.__class__.__name__



class EPG_chat(BaseModel):
    eventid: int
    title: str
    description: Optional[str] = None
    contentinfo: Optional[List[str]] = None
    event: Optional[str] = None





class TVEvent(BaseModel):
    epg_entry:EPG
    movies:Optional[list[Tmdb_Movie]] = Field(default_factory=list)
    series:Optional[list[TVSerial]] = Field(default_factory=list)

    

# -------------- Batch Result -----------------------------------



# class Candidate(BaseModel):
#     """
#     A single TMDB candidate returned by the batch job.
#     """
#     tmdb_title: str = Field(..., description="Title of the TMDB entry")
#     tmdb_id: int = Field(..., description="TMDB identifier")
#     eventid: str = Field(..., description="EPG event identifier")
#     probability: float = Field(..., ge=0.0, le=1.0, description="Model-assigned probability that this is the correct match")
#     reasoning: str = Field(..., description="Human-readable explanation for the assigned probability")


# class ChoiceMessage(BaseModel):
#     """
#     The message object nested inside a completion choice.
#     """
#     role: str
#     content: str


# class Choice(BaseModel):
#     """
#     A single choice returned by the chat completion.
#     """
#     index: int
#     message: ChoiceMessage
#     finish_reason: str


# class Usage(BaseModel):
#     """
#     Token-usage statistics for the request.
#     """
#     prompt_tokens: int
#     completion_tokens: int
#     total_tokens: int


# class ResponseBody(BaseModel):
#     """
#     The body of the HTTP response, i.e. a standard OpenAI-style chat completion.
#     """
#     id: str
#     object: str
#     created: int
#     model: str
#     choices: List[Choice]
#     usage: Usage
#     system_fingerprint: Optional[str] = None


# class ResponseEnvelope(BaseModel):
#     """
#     The `response` object inside the top-level batch result.
#     """
#     status_code: int
#     request_id: str
#     body: ResponseBody


# class BatchResult(BaseModel):
#     """
#     Root object returned by an OpenAI batch job.
#     """
#     id: str
#     custom_id: str
#     response: ResponseEnvelope
#     error: Optional[str] = None

#     # ------------------------------------------------------------------
#     # Helper to quickly get the parsed `Candidate` list out of the JSON
#     # ------------------------------------------------------------------
#     def parsed_candidates(self) -> List[Candidate]:
#         """
#         Parse the JSON string inside `response.body.choices[0].message.content`
#         into a list of `Candidate` objects.
#         """
#         import json

#         content = self.response.body.choices[0].message.content
#         return [Candidate(**item) for item in json.loads(content)]


# -------------- Serial and Episode -----------------------------------

class _SerEpisode_chat(BaseModel):
    episode_number: int
    id: int
    name: str
    overview: str
    season_number: int

class Serial_chat(BaseModel):
    id: int
    name: str
    overview: str
    episodes: List[_SerEpisode_chat] = Field(default_factory=list)

    class Config:
        extra = 'ignore'  # Ignoriere zusätzliche Felder


# -------------- MovieSmall  -----------------------------------

class Movie_chat(BaseModel):
    id: int
    title: str
    overview: Optional[str] = None
    release_date: Optional[date] = None
    original_title: Optional[str] = None
    cast_list: Optional[List[str]] = []
    keywords: Optional[List[str]] = []
    languages: Optional[List[str]] = []
    genres: Optional[List[str]] = []

  
    class Config:
        extra = 'ignore'  # Ignoriere zusätzliche Felder



# class Message(BaseModel):
#     role: str
#     content: str

# -------------------  Batch Data ---------------------------------

class BatchInfo(BaseModel):
    customid: str
    messages: List[dict[str, str]]