from typing import Optional
import app.config as cfg
from app.my_types import EPGFilter
from app.filter import (
    TitleBlacklstFilter,
    DaysFilter,
    DurationFilter,
    IsTVChannelFilter,
    KeywordFilter,
    ContentMovieFilter,
    HasTimerFilter
)
from app.mediasrv_ctrl import MS_ControllerBase
from app.services.ms_types import MS_Timer

filter_dict:dict[str, type] = {
    cls.__name__: cls for cls in 
            [
            TitleBlacklstFilter,
            DaysFilter,
            DurationFilter,
            IsTVChannelFilter,
            KeywordFilter,
            ContentMovieFilter,
            HasTimerFilter
            ]
    }


def create_filter(filter_name: str, settings: cfg.Settings) -> Optional[EPGFilter]:
    if (cls := filter_dict.get(filter_name)):
        if filter_name in settings.epg_filter.keys():
            arg = settings.epg_filter[filter_name]
            return cls(arg) if arg else cls()
    return None



def base_filters(settings:cfg.Settings,timers:list[MS_Timer]):
    baselst = ["DaysFilter",
               "IsTVChannelFilter",
               "DurationFilter",
               "TitleBlacklstFilter",
               "KeywordFilter"]
               #"HasTimerFilter"]
    filters = []
    for filter_name in baselst:
        if (f:=create_filter(filter_name, settings)):
            filters.append(f)
    if "HasTimerFilter" in settings.epg_filter.keys():
        filters.append(HasTimerFilter(timers=timers, find_timer=MS_ControllerBase.find_timer))
    return filters
