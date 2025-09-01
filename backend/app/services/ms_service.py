from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from functools import lru_cache
from typing import Any, List, Tuple
from functools import lru_cache
from httpx._models import Response
from urllib.parse import urljoin
import httpx 
from httpx import Client, AsyncClient
from .ms_transformers import xml_to_epglst, xml_to_channellst,  xml_to_timerlst
from .ms_types import MS_Channel, MS_Timer, MS_Epg, TimerParams
from pathlib import Path
from typing import Any, Optional



class AbstractMediaServer(ABC):
    """Abstrakte Basisklasse für alle Media-Server-Clients (echt oder gemockt)."""

    # Konstanten bleiben hier, damit Unterklassen sie nutzen können
    TIMER_LST = "/api/timerlist.html"
    TIMER_ADD = "/api/timeradd.html"
    CHANNEL_LST = "/api/getchannelsxml.html"
    EPG_LST = "/api/epg.html"
    VERSION = "/api/version.html"

    # ------------------------------------------------------------------
    # Abstrakte Methoden (die jede konkrete Klasse implementieren muss)
    # ------------------------------------------------------------------
    @abstractmethod
    def channel_lst(
        self,
        tvonly: bool = False,
        favonly: bool = False,
        epgonly: bool = False,
    ) -> List[MS_Channel]:
        """Liefert die Kanalliste."""
        ...

    @abstractmethod
    def timer_lst(self, enabledonly: bool = False) -> List[MS_Timer]:
        """Liefert die Timer-Liste."""
        ...

    @abstractmethod
    def timer_byid(self, timerid: str) -> MS_Timer:
        """Liefert einen einzelnen Timer per ID."""
        ...

    @abstractmethod
    def timer_add(self, tparams: TimerParams) -> dict:
        """Fügt einen neuen Timer hinzu."""
        ...

    @abstractmethod
    def epg_lst(self, favonly: bool = False) -> List[MS_Epg]:
        """Liefert die EPG-Daten."""
        ...

    @abstractmethod
    def version(self) -> str:
        """Liefert die Server-Version."""
        ...

    @abstractmethod
    def currentdatetime(self) -> datetime:
        """ gibt die aktuelle Zeit zurück"""
        ...

    @abstractmethod
    def close(self) -> None:
        """Schließt offene Verbindungen / Ressourcen."""
        ...

    # Kontext-Manager bleibt *unverändert* erhalten
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ===================================================================
# 2. Konkrete Produktiv-Implementierung 
# ===================================================================
class MediaServer(AbstractMediaServer):
    def __init__(self, httpclient:httpx.Client, url: str, debug: bool = False) -> None:
        self.base_url = url
        self.debug = debug
        self.rawtext = ""
        self.client = httpclient


    # ------------- interne Helfer (nicht Teil des öffentlichen ABC) -------------
    def _client_get(self, endpoint: str, params: dict) -> Response:
        url = urljoin(self.base_url, endpoint)

        response: Response = self.client.get(url=url, params=params) # type: ignore
        if self.debug:
            self.rawtext = response.text
        return response
    

    def _tv_channels(self, params: dict) -> List[MS_Channel]:
        response = self._client_get(endpoint=self.CHANNEL_LST, params=params)
        response.raise_for_status()
        dictlst = xml_to_channellst(response.text)
        return [MS_Channel.model_validate(d) for d in dictlst]

    def _timer_lst(self, enabledonly: bool = False) -> List[dict]:
        params = {"utf8": 2}
        if enabledonly:
            params["enabledonly"] = 1
        response = self._client_get(endpoint=self.TIMER_LST, params=params)
        response.raise_for_status()
        return xml_to_timerlst(response.text)

    def _epgs(self, favonly: bool = False) -> List[dict]:
        params: dict[str, Any] = {"lvl": 2}
        if favonly:
            favchannels = self.channel_lst(favonly=True)
            params["ch"] = ",".join(c.epgid for c in favchannels)
        response = self._client_get(endpoint=self.EPG_LST, params=params)
        response.raise_for_status()
        return xml_to_epglst(response.text)

    # ------------- öffentliche Schnittstelle (implementiert ABC) -------------
    @lru_cache(maxsize=10)
    def channel_lst(
        self, tvonly: bool = False, favonly: bool = False, epgonly: bool = False
    ) -> List[MS_Channel]:
        flags = {"tvonly": tvonly, "favonly": favonly, "epgonly": epgonly}
        params = {k: "1" for k, v in flags.items() if v}
        return self._tv_channels(params=params)

    def timer_lst(self, enabledonly: bool = False) -> List[MS_Timer]:
        return [MS_Timer.model_validate(d) for d in self._timer_lst(enabledonly=enabledonly)]

    def timer_byid(self, timerid: str) -> MS_Timer:
        params = {"utf8": 2, "id": timerid}
        response = self._client_get(endpoint=self.TIMER_LST, params=params)
        response.raise_for_status()
        return MS_Timer.model_validate(xml_to_timerlst(response.text)[0])

    def timer_add(self, tparams: TimerParams) -> dict:
        params = tparams.model_dump(exclude_none=True)
        response = self._client_get(endpoint=self.TIMER_ADD, params=params)
        response.raise_for_status()
        # if an 'already exists' error occured a response header is returned 
        headeritems = dict(response.headers.items())  
        duperror =  headeritems.get('x-already-covered',[])
        timerlst = xml_to_timerlst(response.text) if response.text else []
        return {'duperror': duperror,'timerlst':timerlst}

    def epg_lst(self, favonly: bool = False) -> List[MS_Epg]:
        return [MS_Epg.model_validate(d) for d in self._epgs(favonly=favonly)]

    def version(self) -> str:
        response = self._client_get(endpoint=self.VERSION, params={})
        response.raise_for_status()
        return response.text
    
    def currentdatetime(self) -> datetime:
        return datetime.now()


    def __enter__(self):
        return self  # Wird als `as`-Variable zurückgegeben

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup-Code (z. B. Ressourcen freigeben)
        # Optional: Exceptions behandeln
        if exc_type is not None:
            print(f"Fehler aufgetreten: {exc_val}")
        return False  # True = Exception wird unterdrückt

    def close(self) -> None:
        ...





class AsyncMediaServer(AbstractMediaServer):
    def __init__(self, httpclient: httpx.AsyncClient, url: str, debug: bool = False) -> None:
        self.base_url = url
        self.debug = debug
        self.rawtext = ""
        self.client = httpclient

    # ------------- interne Helfer (asynchron) -------------
    async def _client_get(self, endpoint: str, params: dict) -> httpx.Response:
        url = urljoin(self.base_url, endpoint)
        response = await self.client.get(url=url, params=params)
        if self.debug:
            self.rawtext = response.text
        return response

    async def _tv_channels(self, params: dict) -> List[MS_Channel]:
        response = await self._client_get(endpoint=self.CHANNEL_LST, params=params)
        response.raise_for_status()
        dictlst = xml_to_channellst(response.text)
        return [MS_Channel.model_validate(d) for d in dictlst]

    async def _timer_lst(self, enabledonly: bool = False) -> List[dict]:
        params = {"utf8": 2}
        if enabledonly:
            params["enabledonly"] = 1
        response = await self._client_get(endpoint=self.TIMER_LST, params=params)
        response.raise_for_status()
        return xml_to_timerlst(response.text)

    async def _epgs(self, favonly: bool = False) -> List[dict]:
        params: dict[str, Any] = {"lvl": 2}
        if favonly:
            favchannels = await self.channel_lst(favonly=True)
            params["ch"] = ",".join(c.epgid for c in favchannels)
        response = await self._client_get(endpoint=self.EPG_LST, params=params)
        response.raise_for_status()
        return xml_to_epglst(response.text)

    # ------------- öffentliche Schnittstelle (asynchron) -------------

    async def channel_lst(
        self, tvonly: bool = False, favonly: bool = False, epgonly: bool = False
    ) -> List[MS_Channel]:
        flags = {"tvonly": tvonly, "favonly": favonly, "epgonly": epgonly}
        params = {k: "1" for k, v in flags.items() if v}
        return await self._tv_channels(params=params)

    async def timer_lst(self, enabledonly: bool = False) -> List[MS_Timer]:
        return [MS_Timer.model_validate(d) for d in await self._timer_lst(enabledonly=enabledonly)]

    async def timer_byid(self, timerid: str) -> MS_Timer:
        params = {"utf8": 2, "id": timerid}
        response = await self._client_get(endpoint=self.TIMER_LST, params=params)
        response.raise_for_status()
        return MS_Timer.model_validate(xml_to_timerlst(response.text)[0])

    async def timer_add(self, tparams: TimerParams) -> dict:
        params = tparams.model_dump(exclude_none=True)
        response = await self._client_get(endpoint=self.TIMER_ADD, params=params)
        response.raise_for_status()
        headeritems = dict(response.headers.items())
        duperror = headeritems.get('x-already-covered', [])
        timerlst = xml_to_timerlst(response.text) if response.text else []
        return {'duperror': duperror, 'timerlst': timerlst}

    async def epg_lst(self, favonly: bool = False) -> List[MS_Epg]:
        return [MS_Epg.model_validate(d) for d in await self._epgs(favonly=favonly)]

    async def version(self) -> str:
        response = await self._client_get(endpoint=self.VERSION, params={})
        response.raise_for_status()
        return response.text

    async def currentdatetime(self) -> datetime:
        return datetime.now()

    async def close(self) -> None:
        await self.client.aclose()

# ===================================================================
# 3. Mock-Implementierung – liefert nur statische Fixtures
# ===================================================================
class MockMediaServer(AbstractMediaServer):
    """
    Stellt vorgehaltene Daten bereit und simuliert Netzwerk-Zugriffe.
    """

    def __init__(
        self,
        *,
        channels: List[MS_Channel] | None = None,
        timers: List[MS_Timer] | None = None,
        epgs: List[MS_Epg] | None = None,
        version: str = "9.9.9-mock",
    ) -> None:
        # Kein Client, keine URL – nur die Fixtures
        self._channels = channels or []
        self._timers = timers or []
        self._epgs = sorted(epgs or [], key=lambda epg: epg.start)
        self._startdate = self._epgs[0].start if self._epgs else datetime.now()
        self._version = version

    # ------------- öffentliche Schnittstelle (implementiert ABC) -------------
    @lru_cache(maxsize=10)
    def channel_lst(
        self, tvonly: bool = False, favonly: bool = False, epgonly: bool = False
    ) -> List[MS_Channel]:
        # returns always the complete list
        return self._channels.copy()


    def timer_lst(self, enabledonly: bool = False) -> List[MS_Timer]:
        if enabledonly:
            return [t for t in self._timers if t.enabled]
        return self._timers.copy()

    def timer_byid(self, timerid: str) -> MS_Timer:
        # for t in self._timers:
        #     if t.id == timerid:
        #         return t
        raise NotImplementedError(f"Timer {timerid!r} not found")

    def timer_add(self, tparams: TimerParams) -> dict:
        # Einfache „Erfolg“-Antwort, keine echte Persistenz
        return {'duperror': [],'timerlst':[{"id": "mock123", "state": "added"}]}
        #return (200, [{"id": "mock123", "state": "added"}])

    def epg_lst(self, favonly: bool = False) -> List[MS_Epg]:
        if favonly:
            favids = {c.epgid for c in self.channel_lst(favonly=True)}
            result = [e for e in self._epgs if e.channel in favids]
            return result
        return self._epgs.copy()

    def version(self) -> str:
        return self._version
    
    def currentdatetime(self) -> datetime:
        return self._startdate   

    def close(self) -> None:
        # Nichts zu tun – es gibt keinen echten Client
        pass

    # Kontext-Manager wird von der Basisklasse geerbt