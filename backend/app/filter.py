
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Any, Callable



from .services.tmdb_types import TVSearchResult
from .my_types import EPG, EPGFilter
from .epg_categorie import is_movie
from .mediasrv_ctrl import MS_ControllerBase


# --------------------- EPG filter ---------------------------


class TitleBlacklstFilter(EPGFilter):
    def __init__(self, filepath:Path|str):
        if isinstance(filepath,str):
            filepath = Path(filepath)
        self.filepath = filepath
        self.blacklist = filepath.read_text(encoding='utf-8').split('\n')

    def __call__(self, epg:EPG) -> bool:
        for entry in self.blacklist:
            if entry.endswith('*'):
                if epg.title.startswith(entry[:-1]):
                    return False
            else:
                if entry == epg.title:
                    return False
        return True
    
    def __str__(self) -> str:
        return 'Blacklst ' + self.filepath.name
    

class DurationFilter(EPGFilter):
    def __init__(self, duration:int):
        self.duration = duration

    def __call__(self, epg:EPG) -> bool:
        return epg.duration >= self.duration
    
    def __str__(self) -> str:
        return 'Duration ' + str(self.duration)
      

class IsTVChannelFilter(EPGFilter):
    def __init__(self):
        pass

    def __call__(self, epg:EPG) -> bool:
        if epg.contentinfo:
            return epg.ismovie       
        return MS_ControllerBase.is_tv_channel(int(epg.tv_channel))
    
    def __str__(self) -> str:
        return 'IsTVChannel'

    
class ContentMovieFilter(EPGFilter):
    def __init__(self):
        pass

    def __call__(self, epg:EPG) -> bool:
        if epg.contentinfo:
            return epg.ismovie       
        return is_movie(epg.content)
    
    def __str__(self) -> str:
        return 'IsMovie'


class DaysFilter(EPGFilter):
    def __init__(self,days:int=7, start:datetime|None=None):
        if start:
            self.start = start
        else:
            self.start = datetime.now()
        self.end = self.start + timedelta(days=days)

    def __call__(self, epg:EPG) -> bool:
        return epg.start > self.start and epg.stop <= self.end
    
    def __str__(self) -> str:
        return f'Week {self.start.strftime("%Y-%m-%d")}-{self.end.strftime("%Y-%m-%d")}'
    


class HasTimerFilter (EPGFilter):
    def __init__(self, timers:list,find_timer:Callable):
        self.timers = timers
        self.find_timer = find_timer


    def __call__(self, epg:EPG) -> bool:
        found = self.find_timer(epg, self.timers)
        return len(found) == 0

    def __str__(self):
        return 'HasTimer'
    

class KeywordFilter (EPGFilter):
    def __init__(self, keywords:list|str):
        if isinstance(keywords,str):
            keywords = keywords.split(',')
        self.keywords = keywords


    def __call__(self, epg:EPG) -> bool:
        for keyword in self.keywords:
            if keyword in epg.title or keyword in epg.event:
                return False
        return True
    
    def __str__(self):
        return f'Has Keywords {",".join(self.keywords)}'
    



# ------------------ TVSearchResult --------------------------

class NameFilter:
    def __init__(self, name:str):
        self.name = name

    def __call__(self, tvresult:TVSearchResult) -> bool:
        if len(tvresult.name) < len(self.name):
            return self.name.startswith(tvresult.name)
        else: 
            return tvresult.name.startswith(self.name)
        
class TitleFilter:
    def __init__(self, title:str):
        self.title = title

    def __call__(self, tvresult:TVSearchResult) -> bool:
        return self.title in tvresult.name
    


# def filterby_title(movielst:list[movie.Movie],title:str) -> list[movie.Movie]:
#     title = xstr.convert_roman(title)
#     title = xstr.unified_sentence(title,tolower=True)
#     result:list[movie.Movie] = []
#     for m in movielst:
#         movie_title:str = xstr.convert_roman(m.title)
#         movie_title = xstr.unified_sentence(movie_title,tolower=True)
#         if movie_title.startswith(title):
#            result.append(m)
#     return result