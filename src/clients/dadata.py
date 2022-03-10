import os

from dadata import Dadata
from dotenv import load_dotenv

from ..models.legal_entity import LegalEntity

load_dotenv()


__all__ = [
    'get_by_inn',
]


def get_by_inn(inn: str) -> list[LegalEntity]:
    with Dadata(os.getenv('DADATA_TOKEN'), os.getenv('DADATA_SECRET')) as dadata_client:
        return [LegalEntity.from_dadata_response(response) for response in dadata_client.find_by_id(name='party', query=inn)]


if __name__ == '__main__':
    result = get_by_inn('7722496158')

    print(result)  # noqa
