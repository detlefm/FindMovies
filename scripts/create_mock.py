from pathlib import Path
import httpx
# import backend.app.config as cfg
# from backend.app.config import init_config
from backend.app.services.ms_service import MediaServer
from backend.app.utils import write_jsonl


# cfg.init_config()
# settings = cfg.settings


def create_backupdata(path:Path):
    with httpx.Client() as http:
        ms   = MediaServer(httpclient=http,url='http://localhost:8089')
        channels = ms.channel_lst()
        timers = ms.timer_lst()
        epgs = ms.epg_lst(favonly=True)
        write_jsonl(filepath=path / 'channels.jsonl',data=[c.model_dump(mode='json',by_alias=True) for c in channels])
        write_jsonl(filepath=path / 'timers.jsonl',data=[t.model_dump(mode='json',by_alias=True) for t in timers])
        write_jsonl(filepath=path / 'epgs.jsonl',data=[e.model_dump(mode='json',by_alias=True) for e in epgs])

if __name__ == '__main__':
    create_backupdata(path=Path('data/mockdata'))


