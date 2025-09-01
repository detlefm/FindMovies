# import os
# from typing import Optional
from .services.tmdb_types import TVSerial
# from .services.ms_types import MS_Timer
# from . import config as cfg
# from .services.chat_service import ChatClient
from .my_types import Movie_chat, Serial_chat, Tmdb_Movie, EPG,  EPG_chat
import re



def shrink_tmdb_movie(movie:Tmdb_Movie) -> Movie_chat:
    return Movie_chat.model_validate(movie.model_dump(exclude_none=True))
 


def shrink_epg(epg:EPG) -> EPG_chat:
    """Returns a shrinked dictionary representation of the EPG entry."""
    description = re.sub(r'\[PDC.*?\]', '', epg.description).strip()

    d:dict = {
        "eventid": epg.eventid,
        'title': epg.title,
        'description': description if description else None,
        'contentinfo': epg.contentinfo if epg.contentinfo else None,
        'event': epg.event if epg.event else None,
    }
    return EPG_chat.model_validate({k: v for k, v in d.items() if v})


def shrink_serial(serial:TVSerial) -> Serial_chat:
    return Serial_chat.model_validate(serial.model_dump(exclude_none=True))
    
