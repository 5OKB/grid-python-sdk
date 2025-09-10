from .company import Company, company_from_dict
from .tle import Tle, tle_from_dict, tle_to_dict


class Satellite:
    def __init__(self, id: int, name: str, tle: Tle, ksy: str, company: Company):
        self._id = id
        self._name = name
        self._tle = tle
        self._ksy = ksy
        self._company = company

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def tle(self) -> Tle:
        return self._tle

    @property
    def ksy(self) -> str:
        return self._ksy

    @property
    def company(self) -> Company:
        return self._company

    def __eq__(self, other):
        return self.id == other.id

    def to_dict(self) -> dict:
        res = {'id': int(self.id)}
        if self.name:
            res['name'] = self.name
        if isinstance(self.tle, Tle):
            res['tle'] = tle_to_dict(self.tle)
        if self.ksy:
            res['ksy'] = self.ksy
        if isinstance(self.company, Company):
            res['company'] = self.company.to_dict()
        return res


def satellite_from_dict(sat_dict: dict) -> Satellite:
    if 'id' not in sat_dict:
        raise ValueError('id is missing for satellite')
    return Satellite(
        id=sat_dict['id'],
        name=sat_dict['name'] if 'name' in sat_dict else None,
        tle=tle_from_dict(sat_dict['tle']) if 'tle' in sat_dict else None,
        ksy=sat_dict['ksy'] if 'ksy' in sat_dict else '',
        company=company_from_dict(sat_dict['company']) if 'company' in sat_dict else None,
    )
