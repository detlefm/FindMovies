# tmdb_service_en.py
from functools import lru_cache
from typing import Optional
from httpx import AsyncClient,Client
import asyncio
import os

BASE_URL = "https://api.themoviedb.org/3"
DEFAULT_LANGUAGE = "de-DE"   # still defaulting to German locale — change if desired


class Tmdb_Srv:
    """
    Synchronous TMDB API client.

    Uses the synchronous `HttpClient` for all HTTP requests.

    Args
    ----
    api_token : str
        Your TMDB API key (v3 auth).
    """

    def __init__(self,httpclient:Client, api_token:Optional[str] = None, language:str = DEFAULT_LANGUAGE):
        tmdb_token = api_token if api_token else os.getenv('TMDB_TOKEN','')
        if not tmdb_token:
            raise ValueError('TMDB_TOKEN not set')
        self.headers = {"accept": "application/json","Authorization": f"Bearer {tmdb_token}"}
        self.base_url = BASE_URL
        self.client = httpclient
        self.language = language


    # ------------------------------------------------------------------
    # Genres
    # ------------------------------------------------------------------
    @lru_cache(maxsize=10)
    def get_genres(self) -> dict:
        """
        Retrieve the full list of movie genres.

        Returns
        -------
        dict
            Mapping of genre_id -> localized genre name.

        Raises
        ------
        httpx.HTTPStatusError
            If the API call fails.
        """
        response = self.client.get(
            "/genre/movie/list",
            params={"language": self.language},
            headers=self.headers
        )
        return {item["id"]: item["name"] for item in response.json()["genres"]}

    # ------------------------------------------------------------------
    # Movies
    # ------------------------------------------------------------------
    def movies_search(self, query: str) -> list[dict]:
        """
        Search for movies by title.

        Args
        ----
        query : str
            The movie title (or part of it) to search for.

        Returns
        -------
        list[dict]
            Basic metadata for each matching movie.

        Raises
        ------
        httpx.HTTPStatusError
            If the API call fails.
        """
        response = self.client.get(
            "/search/movie",
            params={"query": query, "language": self.language},
            headers=self.headers
        )
        return response.json().get("results", [])

    def movie_details(self, movie_id: int) -> dict:
        """
        Fetch extended details for a single movie.

        Includes top-billed cast, keywords, and available translations.

        Args
        ----
        movie_id : int
            TMDB ID of the movie.

        Returns
        -------
        dict
            {
              "cast_list": [{"name": str, "character": str}, ...],
              "keywords": [str, ...],
              "languages": [str, ...]   # ISO-639-1 codes
            }

        Raises
        ------
        httpx.HTTPStatusError
            If any of the underlying API calls fail.
        """
        credits = self.client.get(
            f"/movie/{movie_id}/credits",
            params={"language": self.language},
            headers=self.headers
        ).json()

        keywords = self.client.get(f"/movie/{movie_id}/keywords").json()

        translations = self.client.get(f"/movie/{movie_id}/translations").json()

        return {
            "cast_list": [
                {"name": actor["name"], "character": actor.get("character", "")}
                for actor in credits.get("cast", [])[:10]
            ],
            "keywords": [kw["name"] for kw in keywords.get("keywords", [])],
            "languages": [
                t["iso_639_1"] for t in translations.get("translations", [])
            ]
        }

    # ------------------------------------------------------------------
    # TV Series
    # ------------------------------------------------------------------
    def tv_search(self, query: str, page: int = 1) -> dict:
        """
        Search for TV series by title.

        Args
        ----
        query : str
            Series title (or part of it) to search for.
        page : int, default 1
            Page number of paginated results.

        Returns
        -------
        dict
            Full API response including `results`, `total_pages`, etc.

        Raises
        ------
        httpx.HTTPStatusError
            If the API call fails.
        """
        response = self.client.get(
            "/search/tv",
            params={
                "query": query,
                "page": page,
                "include_adult": "true",
                "language": self.language
            },
            headers=self.headers
        )
        return response.json()

    def tv_byid(self, series_id: int) -> dict:
        """
        Retrieve detailed information for a single TV series.

        Args
        ----
        series_id : int
            TMDB ID of the series.

        Returns
        -------
        dict
            Complete series metadata (name, overview, seasons, etc.).

        Raises
        ------
        httpx.HTTPStatusError
            If the API call fails.
        """
        response = self.client.get(
            f"/tv/{series_id}",
            params={"language": self.language},
            headers=self.headers
        )
        return response.json()

    # ------------------------------------------------------------------
    # TV Seasons
    # ------------------------------------------------------------------
    def tv_season_byid(self, series_id: int, season: int = 1) -> dict:
        """
        Retrieve details for a specific season of a TV series.

        Args
        ----
        show_id : int
            TMDB ID of the parent TV series.
        season : int, default 1
            Season number (1-based).

        Returns
        -------
        dict
            Season metadata including episodes, air dates, etc.

        Raises
        ------
        httpx.HTTPStatusError
            If the API call fails.
        """
        response = self.client.get(
            f"/tv/{series_id}/season/{season}",
            params={"language": self.language},
            headers=self.headers
        )
        return response.json()


