from app.my_types import EPG, EPGFilter


class SpecialFilter(EPGFilter):
    def __init__(self, value:int):
        self.value = value

    def __call__(self, epg:EPG) -> bool:
        return True
    
    def __str__(self) -> str:
        return 'SpecialFilter ' + str(self.value)


def create() -> SpecialFilter:
    return SpecialFilter(value=10)