#!/usr/bin/env python3
"""
CLI-Wrapper für das bestehende Modul.

Aufruf:
    python findmovies.py [GLOBAL_OPTS] collect   [OPTS]
    python findmovies.py [GLOBAL_OPTS] createtimer [OPTS]
"""

import asyncio
from datetime import datetime
import importlib
import importlib.util
import logging
import os
import json
from pathlib import Path
from typing import Generator, Optional
from fastapi import HTTPException
import httpx

import click
from dotenv import load_dotenv

from app.factory import  create_sync_chat_client
from app.chat_prompts import epg_content_prompt
from app.filter import (
    TitleBlacklstFilter,
    ContentMovieFilter,
    DurationFilter,
    KeywordFilter,
    HasTimerFilter,
    DaysFilter,
)
from app.mediasrv_ctrl import MS_Controller, MS_ControllerBase
from app.services.ms_service import MediaServer, MockMediaServer
from app.my_types import EPG, EPGFilter
from backend.app.chat_ctrl import shrink_epg
from app.utils import read_jsonl, write_jsonl
from app.xstr import remove_umlaute
import app.config as cfg
from app.epgfilter_ctrl import base_filters
from app.services.chat_service import AsyncChatClient, ChatClient
from backend.app.factory import create_sync_controller


# ----------------- Bootstrap -----------------
load_dotenv()
cfg.init_config()



data_path = Path(cfg.settings.data_folder)
std_movies_path = data_path / "movies_epgs.jsonl"
logpath: str = cfg.settings.log_folder or cfg.settings.data_folder or "./logs"
logfilename = Path(logpath) / "app.log"

# Root-Logger einmalig konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelno)s] %(message)s",
    datefmt="%y-%m-%d %H:%M",
    handlers=[logging.FileHandler(logfilename, encoding="utf-8")],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()  # wird nur bei --output hinzugefügt



# ---------------- Business-Logic -------------
class Chat4ContentInfo:
    def __init__(self, client:ChatClient, prompttxt: str, model: Optional[str] = None):
        self.client = client
        self.model = model or cfg.settings.ai_model
        self.prompttxt = prompttxt

    def _chat(self, epg: EPG) -> str:

        try:
            sepg = shrink_epg(epg)
            jsonstr = sepg.model_dump(mode="json", exclude_none=True, exclude_defaults=True)
        except Exception as e:
            logger.error(f"Error shrinking EPG: {str(e)}")
            logger.error(f"EPG data: {epg.model_dump_json()}")
            return "Other"
        usr_msg = {
            "role": "user",
            "content": self.prompttxt.replace("<EPGENTRY>", json.dumps(jsonstr, ensure_ascii=False)),
        }
        completion = self.client.ask(messages=[usr_msg], model=self.model)
        if asyncio.iscoroutine(completion):
            completion = asyncio.get_event_loop().run_until_complete(completion)
        json_result = self.client.get_result_content(completion=completion)
        try:
            answer: dict = json.loads(json_result.strip())
            return str(answer.get("category", "Other"))
        except json.JSONDecodeError:
            return "Other"

    def __call__(self, epg: EPG) -> list[str]:
        if epg.contentinfo:
            return epg.contentinfo
        category = self._chat(epg)
        logger.info("ChatBot: %s > %s", category, epg.title)
        return [category]


def add_content_category(
    client, epgs: list[EPG], model: Optional[str] = None
) -> list[EPG]:
    cb = Chat4ContentInfo(client=client, prompttxt=epg_content_prompt, model=model)
    idx = 0
    for epg in epgs:
        if epg.contentinfo:
            continue
        idx += 1
        print(f"\r{idx:3}  ", end="", flush=True)
        epg.contentinfo.extend(cb(epg))
    print()
    return epgs

def get_usr_filters(path:Path) -> Generator[EPGFilter, None, None]:
    for file in sorted(path.glob("*.py")):
        module_name = file.stem
        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec) # type: ignore
        spec.loader.exec_module(module) # type: ignore
        if hasattr(module, "create") and callable(getattr(module, "create")):
            filter = module.create()
            yield filter


def collect_movies(dest: Optional[str] = None, model: Optional[str] = None) -> int:

    movies_path = Path(dest) if dest else std_movies_path
    with create_sync_controller(cfg.settings.server_url, debug=False) as ms_ctrl:
        epgs:list[EPG] = []
        try:
            epgs = ms_ctrl.fetch_epgs(favonly=True)
        except httpx.ConnectError as e:
            logger.error(str(e))
            raise HTTPException(status_code=503, detail=f"Connection Error: {cfg.settings.server_url}")

        timers = ms_ctrl.fetch_timers()
        epgs = MS_ControllerBase.filter_epgs(epgs=epgs, filters=base_filters(cfg.settings, timers=timers))
        epgs = sorted(epgs, key=lambda epg: epg.start)
        logger.info("After Filters, found EPGs: %d", len(epgs))
        try:
            client = create_sync_chat_client(settings=cfg.settings, model=model)
            info = client.info()
            logger.info("%s, %s", info.get("provider"), info.get("model"))
            logger.info("add content categories ...")
            no_contentlst = [epg for epg in epgs if not epg.contentinfo]
            add_content_category(client=client, epgs=no_contentlst, model=model)
            epgs = ms_ctrl.apply_filter(epgs, epgfilter=ContentMovieFilter())
        except ValueError as e:
            logger.error(e)
            logger.warning("AI model not configured, skipping content categorization ...")
            # continue without llm support
            # raise HTTPException(status_code=500, detail=str(e))
        logger.info("After LLM, found EPGs: %d", len(epgs))
        usr_filters = list(get_usr_filters(Path(cfg.settings.plugin_folder)))
        if usr_filters:
            logger.info("Applying %d user filters ...", len(usr_filters))
            epgs = MS_ControllerBase.filter_epgs(epgs=epgs, filters=usr_filters)
        logger.info("After user filters, found EPGs: %d", len(epgs))
        epgs = sorted(epgs, key=lambda epg: epg.start)
        write_jsonl(
            filepath=movies_path,
            data=[epg.model_dump(mode="json", exclude_none=True) for epg in epgs],
        )
        logger.info(f"{len(epgs)} Movies saved to %s", movies_path)
        return len(epgs)

# def collect_movies(dest: Optional[str] = None, model: Optional[str] = None) -> None:
#     with httpx.Client() as http:
#         media_server = MediaServer(httpclient=http,url=cfg.settings.server_url)
#         ms_ctrl = MS_Controller(ms_server=media_server)
#         movies_path = Path(dest) if dest else std_movies_path
#         try: 
#             days = cfg.settings.filterparameters.get("days", 7)
#             if isinstance(days,str):
#                 days = int(days)
#             epgs = ms_ctrl.fetch_epgs(favonly=True, filters=[DaysFilter(days=days)])
#         except httpx.ConnectError as e:
#             logger.error(str(e))
#             print(f"Connection Error  {cfg.settings.server_url}")
#             return
#         epgs = sorted(epgs, key=lambda epg: epg.start)
#         epgs = ms_ctrl.filter_epgs(epgs=epgs, filters=_build_filters(ms_ctrl=ms_ctrl))
#         logger.info("Found EPGs: %d", len(epgs))
#         try:
#             client = chat_client(settings=cfg.settings, model=model)
#             info = client.info()
#             logger.info("%s, %s", info.get("provider"), info.get("model"))
#             logger.info("add content categories ...")
#             epgs = add_content_category(client=client, epgs=epgs, model=model)
#         except ValueError as e:
#             logger.error(e)
#             print(f'Error: {e} - no clarification of content categories possible')
#         epgs = ms_ctrl.apply_filter(epgs, epgfilter=ContentMovieFilter())
#         epgs = sorted(epgs, key=lambda epg: epg.start)
#         write_jsonl(
#             filepath=movies_path,
#             data=[epg.model_dump(mode="json", exclude_none=True) for epg in epgs],
#         )
#         logger.info(f"{len(epgs)} Movies saved to %s", movies_path)
#         print(f"{len(epgs)} Movies saved to {movies_path}")



def create_timers(src: Optional[str] = None) -> None:
    movies_path = Path(src) if src else std_movies_path
    if not movies_path.exists():
        logger.warning("no movie epgs found (%s)", movies_path)
        return

    moviesepglst = [EPG.model_validate(d) for d in read_jsonl(movies_path)]
    pre = post = 5
    if cfg.settings.timerparameters:
        pre = cfg.settings.timerparameters.get("pre", 5)
        post = cfg.settings.timerparameters.get("post", 5)
    count = 0
    with httpx.Client() as http:
        media_server = MediaServer(httpclient=http,url=cfg.settings.server_url)
        ms_ctrl = MS_Controller(ms_server=media_server)        

        timers = ms_ctrl.fetch_timers()
        for epg in moviesepglst:
            if ms_ctrl.find_timer(epg, timers=timers):
                logger.info(
                    "Timer already exists %s %s %s",
                    epg.tv_name,
                    epg.start.strftime("%Y-%m-%d %H:%M"),
                    epg.title,
                )
                continue
            ms_ctrl.timer_add(epg, title=remove_umlaute(epg.title), pre=pre, post=post)
            count +=1
            logger.info(
                "Timer created %s %s %s",
                epg.tv_name,
                epg.start.strftime("%Y-%m-%d %H:%M"),
                epg.title,
            )
        print(f"Created {count} timers")


# ---------------- CLI ------------------------
@click.group()
@click.option("--output", is_flag=True, help="Log-Ausgabe auf die Konsole.")
@click.option("--debug", is_flag=True, help="Debug Modus aktivieren.")
@click.pass_context
def cli(ctx, output: bool, debug: bool):
    """CLI-Einstiegspunkt."""
    if output:
        logging.getLogger().addHandler(stream_handler)
    if debug:
        if output:
            logger.info("Debugmode not implemented yet")
        else:
            print('Debugmode not implemented yet')
        


@cli.command()
@click.option(
    "--dest",
    type=click.Path(path_type=Path),
    help="Zieldatei für die gesammelten Movies (default: data/movies_epgs.jsonl).",
)
@click.option(
    "--model",
    help="LLM-Modell, das für die Kategorisierung verwendet wird.",
)
def collect(dest: Optional[Path], model: Optional[str]) -> None:
    """Filme sammeln und kategorisieren."""
    collect_movies(dest=str(dest) if dest else None, model=model)



@cli.command()
@click.option(
    "--src",
    type=click.Path(exists=True, path_type=Path),
    help="Quelldatei mit den Movies (default: data/movies_epgs.jsonl).",
)
def createtimer(src: Optional[Path]) -> None:
    """Timer auf Basis der gesammelten Filme anlegen."""
    create_timers(src=str(src) if src else None)


if __name__ == "__main__":
    cli()