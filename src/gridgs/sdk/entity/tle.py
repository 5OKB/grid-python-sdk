class Tle:
    def __init__(self, line_one: str, line_two: str, norad_id: int):
        self._line_one = line_one
        self._line_two = line_two
        self._norad_id = int(norad_id)

    @property
    def line_one(self) -> str:
        return self._line_one

    @property
    def line_two(self) -> str:
        return self._line_two

    @property
    def norad_id(self) -> int:
        return self._norad_id

    def __composite_values__(self):
        return self.line_one, self.line_two, self.norad_id

    def __eq__(self, other):
        return self.norad_id == other.norad_id


def tle_to_dict(tle: Tle) -> dict:
    if not isinstance(tle, Tle):
        raise ValueError('wrong instance of tle object')
    return {'lineOne': tle.line_one, 'lineTwo': tle.line_two, 'noradId': tle.norad_id}


def tle_from_dict(tle_dict: dict) -> Tle:
    return Tle(line_one=tle_dict['lineOne'], line_two=tle_dict['lineTwo'], norad_id=tle_dict['noradId'])
