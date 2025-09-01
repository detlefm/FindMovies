from app.my_types import EPG, EPGFilter


class WildCardFilter(EPGFilter):
    def __init__(self, strlst: list[str]):
        self.strlst = strlst

    def __call__(self, epg:EPG) -> bool:
        return True
    
    def __str__(self) -> str:
        return 'WildCardFilter ' + str(self.strlst)


def create() -> WildCardFilter:
    return WildCardFilter(strlst=["example"])