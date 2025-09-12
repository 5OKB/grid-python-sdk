class Company:
    def __init__(self, id: int):
        if not id or not id > 0:
            raise ValueError('Company id should be more then 0')
        self._id = id

    @property
    def id(self) -> int:
        return self._id

    def __eq__(self, other):
        return self.id == other.id

    def to_dict(self) -> dict:
        return {'id': self.id}


def company_from_dict(cmp: dict) -> Company:
    return Company(id=cmp['id'])
