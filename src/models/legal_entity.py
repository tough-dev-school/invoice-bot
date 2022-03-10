from dataclasses import asdict
from dataclasses import dataclass


@dataclass
class LegalEntity:
    name: str
    inn: str
    kpp: str

    def __str__(self) -> str:
        return f'{self.name}, ИНН {self.inn}, КПП {self.kpp}'

    @classmethod
    def from_dadata_response(cls, response: dict) -> 'LegalEntity':
        return cls(
            name=response['value'],
            inn=response['data']['inn'],
            kpp=response['data'].get('kpp', 0),
        )

    def to_tinkoff(self) -> dict:
        return asdict(self)
