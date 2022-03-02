from dataclasses import asdict
from dataclasses import dataclass


@dataclass
class LegalEntity:
    name: str
    inn: str
    kpp: str

    @classmethod
    def from_dadata_response(cls, response: dict) -> 'LegalEntity':
        return cls(
            name=response['value'],
            inn=response['data']['inn'],
            kpp=response['data']['kpp'],
        )

    def to_tinkoff(self) -> dict:
        return asdict(self)
