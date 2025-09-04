#!/usr/bin/env python3
"""
FastAPI-Wrapper für das bestehende Modul.
"""
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path
from typing import Optional, List, Generator
import httpx

from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

from app.factory import create_async_chat_client,create_async_controller

from app.chat_prompts import epg_content_prompt
from app.filter import (
    TitleBlacklstFilter,
    ContentMovieFilter,
    DurationFilter,
    KeywordFilter,
    HasTimerFilter,
    DaysFilter,
    IsTVChannelFilter
)
from app.epgfilter_ctrl import base_filters
from app.mediasrv_ctrl import AsyncMS_Controller, MS_Controller, MS_ControllerBase
from app.services.ms_service import AsyncMediaServer, MediaServer, MockMediaServer
from app.services.chat_service import AsyncChatClient, ChatClient
from app.my_types import EPG
from app.chat_ctrl import shrink_epg
from app.utils import read_jsonl, write_jsonl,dt2str
from app.xstr import remove_umlaute
import app.config as cfg
from app.services.ms_types import MS_Timer
import importlib.util
from app.my_types import EPGFilter

import os
import sys

# ----------------- Bootstrap -----------------
load_dotenv()
cfg.init_config()

data_path = Path(cfg.settings.data_folder)
std_movies_path = data_path / "movies_epgs.jsonl"
logpath: str = cfg.settings.log_folder or cfg.settings.data_folder
logfilename = Path(logpath) / "app.log"

# Root-Logger einmalig konfigurieren
# Prüfen, ob in Docker via Umgebungsvariable LOG_TO_STDOUT=true
if os.environ.get("LOG_TO_STDOUT", "false").lower() == "true":
    # In Docker: Log auf stdout
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%y-%m-%d %H:%M",
        stream=sys.stdout,
    )
    logging.info("Logging is configured to stream to stdout.")
else:
    # Lokal: Log in Datei
    logfilename.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelno)s] %(message)s",
        datefmt="%y-%m-%d %H:%M",
        handlers=[logging.FileHandler(logfilename, encoding="utf-8")],
    )
    logging.info(f"Logging is configured to file: {logfilename}")
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

# ----------------- FastAPI Setup -----------------
app = FastAPI(title="Movie Timer API", version="1.0.0")
api_router = APIRouter(prefix="/api")

# CORS konfigurieren (bleibt nützlich, falls Sie die API doch mal von woanders ansprechen)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------- Pydantic Models -----------------
class Info(BaseModel):
    modified: Optional[str] = None
    count: int
    running: bool
    run_started: Optional[str] = None
    run_progress: Optional[float] = None


class TimerStatus(BaseModel):
    created_timers: int
    message: str

class MovieList(BaseModel):
    movies: List[dict]




# -------------------------------------------------
# 1) Module dynamisch laden
# -------------------------------------------------

def get_usr_filters(path:Path) -> Generator[EPGFilter, None, None]:
    for file in sorted(path.glob("*.py")):
        module_name = file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec) # type: ignore
        spec.loader.exec_module(module) # type: ignore
        if hasattr(module, "create") and callable(getattr(module, "create")):
            filter = module.create()
            yield filter

# ---------------- Business-Logic -------------

infostatus = Info(count=0, running=False)

def movies_path() -> Path:
    return std_movies_path

def read_movies() -> list[dict]:
    """Liest die Filmliste aus der JSONL-Datei."""
    if not movies_path().exists():
        raise FileNotFoundError(f"Movie file not found: {movies_path()}")
    return read_jsonl(movies_path())


class Chat4ContentInfo:
    def __init__(self, client: AsyncChatClient, prompttxt: str, model: Optional[str] = None):
        self.client = client
        self.model = model or cfg.settings.ai_model
        self.prompttxt = prompttxt

    async def _chat(self, epg: EPG) -> str:
        sepg = shrink_epg(epg)
        jsonstr = sepg.model_dump(mode="json", exclude_none=True, exclude_defaults=True)
        usr_msg = {
            "role": "user",
            "content": self.prompttxt.replace("<EPGENTRY>", json.dumps(jsonstr, ensure_ascii=False)),
        }
        completion = await self.client.ask(messages=[usr_msg], model=self.model)
        json_result = self.client.get_result_content(completion=completion)
        try:
            answer: dict = json.loads(json_result.strip())
            return str(answer.get("category", "Other"))
        except json.JSONDecodeError:
            return "Other"

    async def __call__(self, epg: EPG) -> list[str]:
        if epg.contentinfo:
            return epg.contentinfo
        category = await self._chat(epg)
        logger.info("ChatBot: %s > %s", category, epg.title)
        return [category]




async def add_content_category(
            client: AsyncChatClient, 
            epgs: list[EPG], 
            model: Optional[str] = None
        ) -> None:
    lenepgs = len(epgs)
    step = 60 / lenepgs if lenepgs > 0 else 1
    cb = Chat4ContentInfo(client=client, prompttxt=epg_content_prompt, model=model)
    idx = 0
    for epg in epgs:
        idx += 1
        logger.info(f"Processing {idx:3} - {epg.title}")
        infostatus.run_progress = 0.15 + (idx * step / 100)
        epg.contentinfo.extend(await cb(epg))
    


async def collect_movies( model: Optional[str] = None) -> int:
    
    async with create_async_controller(cfg.settings.server_url, debug=False) as ms_ctrl:
        infostatus.running = True
        infostatus.run_started = dt2str(datetime.now())
        infostatus.modified = infostatus.run_started
        infostatus.count = 0
        infostatus.run_progress = 0.05
        try:
            epgs = await ms_ctrl.fetch_epgs(favonly=True)
            infostatus.run_progress = 0.1
        except httpx.ConnectError as e:
            logger.error(str(e))
            raise HTTPException(status_code=503, detail=f"Connection Error: {cfg.settings.server_url}")

        timers = await ms_ctrl.fetch_timers()
        epgs = MS_ControllerBase.filter_epgs(epgs=epgs, filters=base_filters(cfg.settings, timers=timers))
        epgs = sorted(epgs, key=lambda epg: epg.start)
        logger.info("After Filters, found EPGs: %d", len(epgs))
        infostatus.run_progress = 0.15
        try:
            client = create_async_chat_client(settings=cfg.settings, model=model)
            info = client.info()
            logger.info("%s, %s", info.get("provider"), info.get("model"))
            logger.info("add content categories ...")
            no_contentlst = [epg for epg in epgs if not epg.contentinfo]
            await add_content_category(client=client, epgs=no_contentlst, model=model)
            epgs = ms_ctrl.apply_filter(epgs, epgfilter=ContentMovieFilter())
        except ValueError as e:
            logger.error(e)
            logger.warning("AI model not configured, skipping content categorization ...")
            # continue without llm support
            # raise HTTPException(status_code=500, detail=str(e))
        logger.info("After LLM, found EPGs: %d", len(epgs))
        infostatus.run_progress = 0.8
        usr_filters = list(get_usr_filters(Path(cfg.settings.plugin_folder)))
        if usr_filters:
            logger.info("Applying %d user filters ...", len(usr_filters))
            epgs = MS_ControllerBase.filter_epgs(epgs=epgs, filters=usr_filters)
        logger.info("After user filters, found EPGs: %d", len(epgs))
        epgs = sorted(epgs, key=lambda epg: epg.start)
        infostatus.run_progress = 0.9
        write_jsonl(
            filepath=movies_path(),
            data=[epg.model_dump(mode="json", exclude_none=True) for epg in epgs],
        )
        logger.info(f"{len(epgs)} Movies saved to %s", movies_path())
        infostatus.running = False
        infostatus.run_started = None
        infostatus.count = len(epgs)
        m_time = datetime.fromtimestamp(movies_path().stat().st_mtime)
        infostatus.modified =  dt2str(m_time)
        infostatus.run_progress = None
        return len(epgs)



async def create_timers() -> int:

    try:
        movies:list[dict] = read_movies()
    except FileNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=str(e))


    moviesepglst = [EPG.model_validate(d) for d in movies]
    pre = post = 5
    if cfg.settings.timerparameters:
        pre = cfg.settings.timerparameters.get("pre", 5)
        post = cfg.settings.timerparameters.get("post", 5)
    
    count = 0
    async with httpx.AsyncClient() as http:
        media_server = AsyncMediaServer(httpclient=http, url=cfg.settings.server_url)
        ms_ctrl = AsyncMS_Controller(ms_server=media_server)
        
        timers = await ms_ctrl.fetch_timers()
        for epg in moviesepglst:
            if MS_ControllerBase.find_timer(epg, timers=timers):
                logger.info(
                    "Timer already exists %s %s %s",
                    epg.tv_name,
                    dt2str(epg.start),
                    epg.title,
                )
                continue
            await ms_ctrl.timer_add(epg, title=remove_umlaute(epg.title), pre=pre, post=post)
            count += 1
            logger.info(
                "Timer created %s %s %s",
                epg.tv_name,
                dt2str(epg.start),
                epg.title,
            )
        return count



# ---------------- API Endpoints (jetzt auf api_router) -----------------
@api_router.post("/collect", summary="Filme sammeln und kategorisieren")
async def api_collect( model: Optional[str] = None):
    """Langlaufende Operation zum Sammeln und Kategorisieren von Filmen."""
    try:
        count = await collect_movies(model=model)
        return {"message": f"Successfully collected {count} movies", "count": count}
    except Exception as e:
        logger.error(f"Error in collect: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@api_router.get("/createtimer", response_model=TimerStatus, summary="Timer erstellen")
async def api_createtimer():
    """Timer auf Basis der gesammelten Filme anlegen."""
    try:
        count = await create_timers()
        return TimerStatus(
            created_timers=count,
            message=f"Successfully created {count} timers"
        )
    except Exception as e:
        logger.error(f"Error in createtimer: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/movies", response_model=List[dict], summary="Filme abrufen")
async def api_get_movies():
    """Liste der gesammelten Filme als JSON zurückgeben."""
    try:
        movies:list[dict] = read_movies()
        return [epg for epg in movies if EPG.model_validate(epg).start > datetime.now()]
    except FileNotFoundError as e:
        logger.warning(str(e))
        raise HTTPException(status_code=404, detail=str(e))    


@api_router.post("/movies", summary="Filme ersetzen")
async def api_update_movies(movies: MovieList):
    """Die vorhandene Filmliste durch neue Daten ersetzen."""

    try:
        write_jsonl(
            filepath=movies_path(),
            data=movies.movies
        )
        return {"message": f"Successfully updated {len(movies.movies)} movies"}
    except Exception as e:
        logger.error(f"Error updating movies: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    

@api_router.get("/info", response_model=dict, summary="Status abrufen")
async def api_get_info():
    """Statusinformationen zur Anwendung abrufen."""
    if infostatus.running:
        return infostatus.model_dump(mode="json")

    infostatus.count = 0
    infostatus.modified =  None    
    try:
        movies:list[dict] = read_movies()
        now = datetime.now() + timedelta(minutes=5)
        movies = [epg for epg in movies if EPG.model_validate(epg).start > now]
        infostatus.count = len(movies)
        m_time = datetime.fromtimestamp(movies_path().stat().st_mtime)
        infostatus.modified = dt2str(m_time)
    except FileNotFoundError as e:
        logger.warning(str(e))

    return infostatus.model_dump(mode="json")


# Binden des API-Routers an die Hauptanwendung
app.include_router(api_router)


# ---------------- Frontend Serving -----------------
# Dieser Teil muss nach dem `include_router` stehen, damit die API-Routen Priorität haben.

# Pfad zum gebauten Frontend
static_files_path = Path(__file__).parent.parent / "frontend" / "dist"

# Dieser Exception-Handler fängt 404-Fehler ab. Das ist wichtig für Single-Page-Applications (SPAs).
# Wenn der Benutzer die Seite bei einer Frontend-Route (z.B. /filme/123) neu lädt,
# würde der Server normalerweise einen 404-Fehler zurückgeben. Stattdessen liefern wir die
# index.html aus, und der Svelte-Router kann die Anfrage clientseitig korrekt behandeln.
@app.exception_handler(404)
async def not_found_exception_handler(request, exc):
    """Gibt bei einem 404-Fehler die index.html des Frontends zurück."""
    # Sicherstellen, dass die index.html existiert, bevor wir sie senden
    index_path = static_files_path / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    else:
        # Fallback, falls die index.html nicht gefunden wird
        logger.error(f"Frontend 'index.html' not found at {index_path}")
        raise exc

# Mounten der statischen Dateien. `html=True` sorgt dafür, dass Anfragen an `/`
# die `index.html` zurückliefern.
app.mount("/", StaticFiles(directory=static_files_path, html=True), name="static")


# ---------------- Main -----------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)