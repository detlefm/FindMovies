from pydantic import BaseModel, Field
from typing import List, Optional, Set
from pydantic import BaseModel, Field, HttpUrl
from datetime import date


# --------- Tmdb_Movie ----------------------------------------------

class CastMember(BaseModel):
    name: str
    character: str

class Tmdb_Movie(BaseModel):
    """Repräsentiert einen Film mit vollständigen TMDB-Informationen."""
    id: int
    title: str
    original_title: str
    overview: str
    release_date: str
    adult: bool
    backdrop_path: Optional[str] = None
    poster_path: Optional[str] = None
    popularity: float
    vote_average: float
    vote_count: int
    video: bool
    original_language: str
    genre_ids: Set[int] = Field(default_factory=set)
    genres: List[str] = Field(default_factory=list)
    cast_list: List[CastMember] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    languages: Set[str] = Field(default_factory=set)
    #all_languages: Set[str] = Field(default_factory=set, exclude=True)
    
    @property
    def combined_languages(self) -> Set[str]:
        """Kombiniert Original- und Übersetzungssprachen."""
        return {self.original_language} | self.languages




# ------------------------ TVEpisode -----------------------------


class CrewMember(BaseModel):
    job: str
    department: str
    credit_id: str
    adult: bool
    gender: int
    id: int
    known_for_department: str
    name: str
    original_name: str
    popularity: float
    profile_path: Optional[str]


class GuestStar(BaseModel):
    character: str
    credit_id: str
    order: int
    adult: bool
    gender: int
    id: int
    known_for_department: str
    name: str
    original_name: str
    popularity: float
    profile_path: Optional[str]


class TVEpisode(BaseModel):
    air_date: Optional[str]
    episode_number: int
    episode_type: str
    id: int
    name: str
    overview: str
    production_code: str
    runtime: Optional[int] =0
    season_number: int
    show_id: int
    still_path: Optional[str]
    vote_average: float
    vote_count: int
    crew: List[CrewMember]
    guest_stars: List[GuestStar]


# ------------------------ TVSerial -----------------------------


class Creator(BaseModel):
    id: int
    name: str
    original_name: str
    gender: int
    profile_path: Optional[str]
    credit_id: str


class Genre(BaseModel):
    id: int
    name: str


class Network(BaseModel):
    id: int
    name: str
    logo_path: Optional[str]
    origin_country: str


class ProductionCompany(BaseModel):
    id: int
    name: str
    logo_path: Optional[str]
    origin_country: str


class ProductionCountry(BaseModel):
    iso_3166_1: str
    name: str


class SpokenLanguage(BaseModel):
    english_name: str
    iso_639_1: str
    name: str


class Season(BaseModel):
    air_date: Optional[date]
    episode_count: int
    id: int
    name: str
    overview: Optional[str]
    poster_path: Optional[str]
    season_number: int
    vote_average: float


class LastEpisodeToAir(BaseModel):
    id: int
    name: str
    overview: str
    vote_average: float
    vote_count: int
    air_date: date
    episode_number: int
    episode_type: str
    production_code: str
    runtime: Optional[int] = 0
    season_number: int
    show_id: int
    still_path: Optional[str]


class TVSerial(BaseModel):
    adult: bool
    backdrop_path: Optional[str]
    created_by: List[Creator]
    episode_run_time: List[int]
    first_air_date: Optional[str] = Field(default='')
    genres: List[Genre]
    homepage: Optional[str|None] = Field(default=None)
    id: int
    in_production: bool
    languages: List[str]
    last_air_date: Optional[str] = Field(default='')
    last_episode_to_air: Optional[LastEpisodeToAir] = Field(default=None)
    name: str
    next_episode_to_air: Optional[str] = None
    networks: List[Network]
    number_of_episodes: int
    number_of_seasons: int
    origin_country: List[str]
    original_language: str
    original_name: str
    overview: str
    popularity: float
    poster_path: Optional[str]
    production_companies: List[ProductionCompany]
    production_countries: List[ProductionCountry]
    seasons: List[Season]
    spoken_languages: List[SpokenLanguage]
    status: str
    tagline: str
    type: str
    vote_average: float
    vote_count: int
    episodes: List[TVEpisode] = Field(default_factory=list)


# ------------------------ TVSearchResult -----------------------------




class TVSearchResult(BaseModel):
    adult: bool
    backdrop_path: str | None = Field(None, description="Full URL via tmdb-image-base")
    genre_ids: List[int]
    id: int
    origin_country: List[str]
    original_language: str
    original_name: str
    overview: str
    popularity: float
    poster_path: str | None = Field(None, description="Full URL via tmdb-image-base")
    first_air_date: str
    name: str
    vote_average: float
    vote_count: int
