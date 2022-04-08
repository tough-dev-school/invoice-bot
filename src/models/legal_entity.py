from dataclasses import asdict
from dataclasses import dataclass


@dataclass
class LegalEntity:
    name: str
    inn: str
    kpp: str | None

    def __str__(self) -> str:
        if self.kpp is None:
            return f'{self.name}, ИНН {self.inn}'
        else:
            return f'{self.name}, ИНН {self.inn}, КПП {self.kpp}'

    @classmethod
    def from_dadata_response(cls, response: dict) -> 'LegalEntity':
        return cls(
            name=response['value'],
            inn=response['data']['inn'],
            kpp=response['data'].get('kpp', None),
        )

    def to_tinkoff(self) -> dict:
        return asdict(self)
