import json
from pydantic import BaseModel, Field, ValidationError
from typing import List
import asyncio
from .services.tmdb_service import Tmdb_Srv
from .services.tmdb_types import Tmdb_Movie,  TVEpisode, TVSerial, TVSearchResult
# from .services.services import get_tmdbservice
import logging


logger = logging.getLogger(__name__)




class TMDB_Controller:
    def __init__(self, service:Tmdb_Srv):
        self.tmdb_service = service



    def movies_find(self, query: str) -> List[Tmdb_Movie]:
        """
        Sucht Filme mit Titel und erstellt detaillierte Movie-Objekte.

        Returns:
            Liste von Tmdb_Movie-Objekten mit vollständigen Informationen
        """
        # Suche nach Filmen
        movies = self.tmdb_service.movies_search(query=query)
        # Genre-Mapping holen
        genre_map = self.tmdb_service.get_genres()

        result = []
        for movie in movies:
            # Detaildaten für diesen Film holen
            details = self.tmdb_service.movie_details(movie['id'])

            # Dictionary für Movie-Daten erstellen
            movie_dict = dict(movie)
            movie_dict.update(details)
            movie_dict["genres"] = [genre_map[gid] for gid in movie.get('genre_ids', []) if gid in genre_map]

            # Tmdb_Movie-Objekt durch direkte Validierung erstellen
            result.append(Tmdb_Movie.model_validate(movie_dict))
        return result


    def tvseries_find(self, query:str) -> list[TVSearchResult]  :
        page = 1
        maxpage = 100
        result = []
        while (page <= maxpage):
            if (pagedict := self.tmdb_service.tv_search(query=query,page=page)):
                maxpage = min(pagedict['total_pages'],100)
                page +=1
                for entry in pagedict['results']:
                    result.append(TVSearchResult.model_validate(entry))
            else:
                break
        return result



    def tvseries_byid(self,id:int) -> TVSerial:
        serial = self.tmdb_service.tv_byid(id)
        tvserial = TVSerial.model_validate(serial)
        eplist:list[TVEpisode] = []

        if (seasons := serial.get('seasons',None)):
            for season in seasons:
                if (seasondetail := self.tmdb_service.tv_season_byid(
                                                series_id=id,
                                                season=season['season_number'])):
                    for episode in seasondetail['episodes']:
                        eplist.append(TVEpisode.model_validate(episode))
            tvserial.episodes = eplist
        return tvserial 


    def tvseries_collect(self, srchresult:list[TVSearchResult]) -> List[TVSerial]:
        tvserieslst = []
        for stubs in srchresult:
            try:
                tvseries = self.tvseries_byid(id=stubs.id)
                tvserieslst.append(tvseries)
            except ValidationError as ex:
                logger.error(f"ValidationError for id={id},{stubs.original_name}, {ex}")
        return tvserieslst        



