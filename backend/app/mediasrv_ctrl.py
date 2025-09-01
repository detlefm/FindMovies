from __future__ import annotations
from datetime import datetime
from typing import Any, Callable, List, Optional
from .epg_categorie import categorie_list
from .services.ms_types import MS_Channel, MS_Epg, MS_Timer, TimerParams
from .services.ms_service import MediaServer, AsyncMediaServer
from .my_types import EPG, EPGFilter
from .xstr import short_str
import logging

logger = logging.getLogger(__name__)


class MS_ControllerBase:
    """
    Enthält nur statische oder kontextunabhängige Methoden.
    """

    @staticmethod
    def msepg_to_epg(ms_epg: MS_Epg, channel: MS_Channel) -> EPG:
        d = {
            'title': next(iter(ms_epg.titles.values()), ''),
            'event': next(iter(ms_epg.events.values()), ''),
            'description': next(iter(ms_epg.descriptions.values()), ''),
            'eventid': ms_epg.eventid,
            'content': ms_epg.content,
            'pdc': ms_epg.pdc,
            'charset': ms_epg.charset,
            'start': ms_epg.start,
            'stop': ms_epg.stop,
            'epgchannel': ms_epg.channel,
            'contentinfo': [item for item in categorie_list(ms_epg.content) if item],
            'tv_channel': channel.channel_id,
            'tv_name': channel.name
        }
        return EPG.model_validate(d)
    
    @staticmethod
    def parse_channel_id(ch: int) -> dict:
        # Konstanten für Bitverschiebungen
        SHIFT_SID            = 0
        SHIFT_APID           = 16
        SHIFT_TUNERTYPE      = 29
        SHIFT_TSID           = 32
        SHIFT_ORBITAL        = 48
        SHIFT_TV_RADIO_FLAG  = 61

        # Masken
        MASK_SID       = (1 << 16) - 1
        MASK_APID      = (1 << (SHIFT_TUNERTYPE - SHIFT_APID)) - 1  # Bits 16-28
        MASK_TUNERTYPE = (1 << (SHIFT_TSID - SHIFT_TUNERTYPE)) - 1  # Bits 29-31
        MASK_TSID      = (1 << (SHIFT_ORBITAL - SHIFT_TSID)) - 1    # Bits 32-47
        MASK_ORBITAL   = (1 << (SHIFT_TV_RADIO_FLAG - SHIFT_ORBITAL)) - 1  # Bits 48-60
        MASK_TV_RADIO  = (1 << (64 - SHIFT_TV_RADIO_FLAG)) - 1      # Bits 61-62 (2 Bit)

        # Zerlegen
        sid       = (ch >> SHIFT_SID) & MASK_SID
        apid      = (ch >> SHIFT_APID) & MASK_APID
        tuner_raw = (ch >> SHIFT_TUNERTYPE) & MASK_TUNERTYPE
        tunertype = tuner_raw - 1  # weil beim Aufbau +1 addiert wurde
        tsid      = (ch >> SHIFT_TSID) & MASK_TSID
        orbital   = (ch >> SHIFT_ORBITAL) & MASK_ORBITAL
        tv_radio  = (ch >> SHIFT_TV_RADIO_FLAG) & MASK_TV_RADIO

        # Tuner-Typen als Konstanten
        # 0 = DVB-C, 1 = DVB-S, 2 = DVB-T, 3 = ATSC, 4 = DVB-IPTV
        if  tunertype > 4:
            tunertype = 5  # Unknown
            
        # TV/Radio-Flag
        tv_radio_result = ['Not defined', 'TV', 'Radio','Unknown'][tv_radio]

        return {
            "sid": sid,
            "apid": apid,
            "tuner_type": tunertype,
            "tuner_name": ["DVB-C", "DVB-S", "DVB-T", "ATSC", "DVB-IPTV","Unknown"][tunertype],
            "transport_stream_id": tsid,
            "orbital_position": orbital / 10.0,  # wieder in Grad
            "tv_radio_flag": tv_radio,
            "tv_radio_result": tv_radio_result
        }

    @staticmethod
    def is_tv_channel(channelid: int) -> bool:
        channel_info = MS_ControllerBase.parse_channel_id(channelid)
        return channel_info.get("tv_radio_flag") == 1

    @staticmethod
    def timer_to_timerparams(timer: MS_Timer) -> TimerParams:
        params: dict[str, Any] = {
            'ch': timer.channel_id,
            'isodate': timer.sdate.strftime("%Y-%m-%d"),
            'isostart': timer.start_datetime.strftime("%H:%M"),
        }

        optional_fields = {
            'action': timer.action,
            'enable': 0 if timer.enabled == '0' else 1,
            'epgevent': int(timer.epg_event_id) if timer.epg_event_id and timer.epg_event_id.isdigit() else None,
            'isostop': timer.stop_datetime.strftime("%H:%M"),
            'pdc': int(timer.pdc) if timer.pdc and timer.pdc.isdigit() else None,
            'post': timer.post_epg if timer.post_epg else None,
            'pre': timer.pre_epg if timer.pre_epg else None,
            'title': timer.description if timer.description else None,
        }

        params.update({k: v for k, v in optional_fields.items() if v is not None})

        watch_it = {
            'pdc': optional_fields.get('pdc'),
            'epgevent': optional_fields.get('epgevent')
        }
        if filtered_watch := {k: v for k, v in watch_it.items() if v}:
            params.update(filtered_watch)
            params['monitorpdc'] = 1

        return TimerParams.model_validate(params)

    @staticmethod
    def epg_to_timerparams(epg: EPG, title: str = '', pre: int = 5, post: int = 5) -> TimerParams:
        d: dict[str, Any] = {
            'ch': epg.tv_channel,
            'isodate': epg.start.strftime("%Y-%m-%d"),
            'isostart': epg.start.strftime("%H:%M"),
            'isostop': epg.stop.strftime("%H:%M"),
            'pre': pre,
            'post': post,
            'title': title,
            'response': '1'
        }
        watch_it = {
            'pdc': epg.pdc if epg.pdc else None,
            'epgevent': epg.eventid if epg.eventid else None
        }
        if filtered_watch := {k: v for k, v in watch_it.items() if v}:
            d.update(filtered_watch)
            d['monitorpdc'] = 1
        return TimerParams.model_validate(d)

    @staticmethod
    def is_outdated(epg: EPG) -> bool:
        return datetime.now() > epg.stop

    @staticmethod
    def find_epg(t: MS_Timer, epgs: List[EPG]) -> List[EPG]:
        return [
            epg for epg in epgs
            if t.channel_id == epg.tv_channel and
            t.start_datetime <= epg.start < t.stop_datetime
        ]

    @staticmethod
    def find_timer(epg: EPG, timers: List[MS_Timer]) -> List[MS_Timer]:
        timerlst = [
            timer for timer in timers
            if epg.tv_channel == timer.channel_id and
            timer.start_datetime <= epg.start < timer.stop_datetime
        ]
        result = []
        for t in timerlst:
            maxstart = max(t.start_datetime, epg.start)
            minstop = min(t.stop_datetime, epg.stop)
            duration = int((minstop - maxstart).total_seconds() / 60)
            percent = duration / epg.duration if epg.duration else 0
            if percent >= 1:
                result.append(t)
        return result

    @staticmethod
    def epg_logentry(epg: EPG) -> str:
        d = {
            'real_id': epg.real_id,
            'title': epg.title,
            'event': epg.event or '',
            'description': epg.description or '',
            'contentinfo': epg.contentinfo or '',
        }
        s = f'{d["real_id"]}, {d["contentinfo"]}, {d["title"]}, {short_str(d["event"], 15)}, {short_str(d["description"], 15)}'
        return s.replace('\n', ' ')

    @staticmethod
    def apply_filter(epgs: List[EPG], epgfilter: EPGFilter) -> list[EPG]:
        result = [epg for epg in epgs if epgfilter(epg)]
        for epg in epgs:
            if not epgfilter(epg):
                logger.info(f'Rejected {MS_ControllerBase.epg_logentry(epg)} | {str(epgfilter)}')
        return result

    @staticmethod
    def filter_epgs(epgs: List[EPG], filters: List[EPGFilter]) -> List[EPG]:
        result = epgs
        for f in filters:
            result = MS_ControllerBase.apply_filter(result, f)
        return result
    


# from typing import List, Optional
# 
# from .services.ms_types import MS_Epg, MS_Timer, TimerParams, MS_Channel
# from .my_types import EPG, EPGFilter


class MS_Controller(MS_ControllerBase):
    def __init__(self, ms_server: MediaServer) -> None:
        self.ms_server = ms_server

    def channel_for_epgid(self, epg_channel_id: str) -> Optional[MS_Channel]:
        channels = self.ms_server.channel_lst(epgonly=True)
        return {c.epgid: c for c in channels}.get(epg_channel_id)

    def fetch_epgs(self, favonly: bool = False, filters: List[EPGFilter] = []) -> List[EPG]:
        filters = filters or []
        epgs = []
        channels = self.ms_server.channel_lst(epgonly=True)
        channel_dict = {c.epgid: c for c in channels}
        for msepg in self.ms_server.epg_lst(favonly=favonly):
            channel = channel_dict.get(msepg.channel)
            if not channel:
                continue
            epgs.append(self.msepg_to_epg(msepg, channel))
        return self.filter_epgs(epgs, filters)

    def fetch_timers(self, enabledonly: bool = False) -> List[MS_Timer]:
        return self.ms_server.timer_lst(enabledonly=enabledonly)

    def timer_add(self, epg: EPG, title: str = '', pre: int = 5, post: int = 5) -> dict:
        tp = self.epg_to_timerparams(epg, title=title, pre=pre, post=post)
        return self.ms_server.timer_add(tp)

    def ms_version(self) -> str:
        return self.ms_server.version()

    def close(self) -> None:
        self.ms_server.close()    




# from typing import List, Optional
# from .services.ms_service import AbstractMediaServer
# from .services.ms_types import MS_Epg, MS_Timer, TimerParams, MS_Channel
# from .my_types import EPG, EPGFilter


class AsyncMS_Controller(MS_ControllerBase):
    def __init__(self, ms_server: AsyncMediaServer) -> None:
        self.ms_server = ms_server

    async def channel_for_epgid(self, epg_channel_id: str) -> Optional[MS_Channel]:
        channels = await self.ms_server.channel_lst(epgonly=True)
        return {c.epgid: c for c in channels}.get(epg_channel_id)

    async def fetch_epgs(self, favonly: bool = False, filters: List[EPGFilter] = []) -> List[EPG]:
        filters = filters or []
        epgs = []
        channels = await self.ms_server.channel_lst(epgonly=True)
        channel_dict = {c.epgid: c for c in channels}
        msepgs = await self.ms_server.epg_lst(favonly=favonly)
        for msepg in msepgs:
            #channel = await self.channel_for_epgid(msepg.channel)
            channel = channel_dict.get(msepg.channel)
            if not channel:
                continue        
            epgs.append(self.msepg_to_epg(msepg, channel))
        return self.filter_epgs(epgs, filters)

    async def fetch_timers(self, enabledonly: bool = False) -> List[MS_Timer]:
        return await self.ms_server.timer_lst(enabledonly=enabledonly)

    async def timer_add(self, epg: EPG, title: str = '', pre: int = 5, post: int = 5) -> dict:
        tp = self.epg_to_timerparams(epg, title=title, pre=pre, post=post)
        return await self.ms_server.timer_add(tp)

    async def ms_version(self) -> str:
        return await self.ms_server.version()

    async def close(self) -> None:
        await self.ms_server.close()        