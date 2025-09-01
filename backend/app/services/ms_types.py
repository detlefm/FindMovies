
from typing import Literal, Optional, Dict
from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator
from datetime import datetime, date, time, timedelta


class MS_Channel(BaseModel):
    nr: str
    name: str
    epgid: str = Field(alias='EPGID')
    flags: int
    channel_id: str = Field(alias='ID')

    model_config = ConfigDict(

        #populate_by_name=True,  # Ersetzt allow_population_by_field_name
        str_strip_whitespace=True,  # Ersetzt anystr_strip_whitespace
        validate_default=True
    )



class TimerChannel(BaseModel):
    id: str = Field(alias='ID')
    epg_id: str = Field(alias='EPGID')

class TimerOptions(BaseModel):
    adjust_pat: str = Field(alias='AdjustPAT')



class MS_Timer(BaseModel):
    description: str = Field(alias='Descr')
    options: TimerOptions = Field(alias='Options')
    format: str = Field(alias='Format')
    folder: str = Field(alias='Folder')
    name_scheme: str = Field(alias='NameScheme')
    title: str = Field(alias='Title')
    subheading: Optional[str] = Field(default='', alias='Subheading')  # Optional gemacht    
    source: str = Field(alias='Source')
    channel: TimerChannel = Field(alias='Channel')
    executable: str = Field(alias='Executeable')  # Korrektur des Typos im JSON
    recording: str = Field(alias='Recording')
    timer_id: str = Field(alias='ID')  # Vermeidung von Konflikt mit Python's id()
    guid: str = Field(alias='GUID')
    timer_type: str = Field(alias='Type')  # Vermeidung von Konflikt mit Python's type()
    enabled: str = Field(alias='Enabled')
    charset: str = Field(alias='Charset')
    pre_epg:Optional[int]= Field(default=0,alias='PreEPG')
    post_epg: Optional[int] = Field(default=0,alias='PostEPG')
    internal_id: str = Field(alias='IntID')
    priority: int = Field(alias='Priority')
    action: str = Field(alias='Action')
    timeshift: str = Field(alias='Timeshift')
    epg_event_id:Optional[str] = Field(default='', alias='EPGEventID')
    pdc:Optional[str] = Field(default='', alias='PDC')
    sdate: date = Field(alias='Date') # Konvertiert "20.07.2025" → date(2025,7,20)
    start: time = Field(alias='Start')  # "23:07:00" → time(23,7,0)
    end: time = Field(alias='End')  # "01:10:00" → time(1,10,0)
    duration: int = Field(alias='Dur')  # "123" → 123 (Minuten)


    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True,
        extra='ignore'
    )

    @field_validator('sdate', mode='before')
    def parse_date(cls, v):
        if isinstance(v, str):
            if v.count('.') == 2:
                # "20.07.2025"
                return datetime.strptime(v, '%d.%m.%Y').date()
            elif v.count('-') == 2:
                # "2025-08-03"
                return datetime.strptime(v, '%Y-%m-%d').date()
        return v

    @field_validator('start', 'end', mode='before')
    def parse_time(cls, v):
        if isinstance(v, str):
            return datetime.strptime(v, '%H:%M:%S').time()
        return v

    @field_validator('duration', mode='before')
    def parse_duration(cls, v):
        if isinstance(v, str):
            return int(v)
        return v    
    
    @computed_field(return_type=str)  # Expliziter Typ für bessere Serialisierung
    @property
    def channel_name(self) -> str:
        """Extrahiert 'ONE HD' aus '2359890668641593480|ONE HD'"""
        return self.channel.id.split('|')[-1].strip()
    
    @property
    def channel_id(self) -> str:
        """Extrahiert '2359890668641593480' aus '2359890668641593480|ONE HD'"""
        tmp = self.channel.id.split('|')
        if len(tmp) > 1:
            return tmp[0]
        else:
            return ''
        #return self.channel.id.split('|')[-1].strip()
    
    @property
    def start_datetime(self) -> datetime:
        return datetime.combine(self.sdate, self.start)
    
    @property
    def stop_datetime(self) -> datetime:
        return self.start_datetime + timedelta(minutes=self.duration)
    


    model_config = ConfigDict(
        populate_by_name=True,  # Erlaubt Nutzung von Original-JSON-Keys via Aliase
        str_strip_whitespace=True,
        extra='ignore'
    )

class TimerAddResult(BaseModel):
    duperror:list[str] = Field(default_factory=list)
    timerlst:list[MS_Timer] = Field(default_factory=list)
    


class MS_Epg(BaseModel):
    eventid: int
    content: int = Field(default=0, exclude=False)
    pdc:int = Field(default=0)
    charset: int
    titles: Dict[str, str]
    events: Dict[str, str] = Field(default_factory=dict)  # Immer Dict, leer falls nicht vorhanden
    descriptions: Dict[str, str] = Field(default_factory=dict)  # Immer Dict, leer falls nicht vorhanden
    start: datetime
    stop: datetime
    channel: str



    @field_validator('start', 'stop', mode='before')
    def parse_datetime(cls, value: str) -> datetime:
        return datetime.strptime(value, "%Y%m%d%H%M%S")

    @field_validator('content', mode='before')
    def parse_content(cls, value: str | None) -> int:
        return int(value) if value is not None else 0

    def model_dump(self, **kwargs) -> dict:
        #kwargs.setdefault('exclude_unset', True)  # Nur gesetzte Felder ausgeben
        data = super().model_dump(**kwargs)
        data["start"] = self.start.strftime("%Y%m%d%H%M%S")
        data["stop"] = self.stop.strftime("%Y%m%d%H%M%S")
        if self.pdc == 0:
            data.pop("pdc", None)
        return data
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y%m%d%H%M%S")
        }



class TimerParams(BaseModel):
    # --- Pflichtfelder (kein Default) ---
    ch: str
    isodate: str
    isostart: str

    # --- Optionale Felder (mit Default) alphabetisch ---
    action: int = 0
    after: Optional[str] = None
    allowdup: Optional[Literal[0, 1]] = None
    audio: Optional[Literal[0, 1]] = None
    days: Optional[str] = None
    eit: Optional[Literal[0, 1]] = None
    enable: int = 1
    encoding: int = 255
    endact: Optional[Literal[0, 1, 2, 3]] = None
    epgevent: Optional[int] = None
    folder: Optional[str] = None
    format: Optional[Literal[0, 1, 2]] = None
    isodur: Optional[str] = None
    isostop: Optional[str] = None
    monforrec: Optional[Literal[0, 1]] = None
    monitorpdc: Optional[Literal[0, 1]] = None
    pdc: Optional[int] = None
    post: Optional[int] = None
    pre: Optional[int] = None
    prio: Optional[int] = None
    response: Optional[str] = None
    scheme: Optional[str] = None
    series: Optional[str] = None
    subs: Optional[Literal[0, 1]] = None
    timeshift: Optional[Literal[0, 1]] = None
    title: Optional[str] = None
    ttx: Optional[Literal[0, 1]] = None



