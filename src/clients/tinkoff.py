import os
from urllib.parse import urljoin

from dotenv import load_dotenv
import httpx

from ..models.item import Item
from ..models.legal_entity import LegalEntity

load_dotenv()

__all__ = [
    'TinkoffException',
    'get_invoice',
]


class TinkoffException(RuntimeError):
    pass


def post(url: str, payload: dict) -> dict:
    response = httpx.post(
        url=urljoin('https://business.tinkoff.ru/openapi/api/', url),
        headers={
            'Authorization': f'Bearer {os.getenv("TINKOFF_INVOICE_TOKEN")}',
        },
        json=payload,
    )

    return response.json()


def get_invoice(legal_entity: LegalEntity, items: list[Item]) -> str:
    result = post(
        url='v1/invoice/send',
        payload={
            'invoiceNumber': '100501',
            'payer': legal_entity.to_tinkoff(),
            'items': [item.to_tinkoff() for item in items],
        },
    )

    if 'errorId' in result:
        raise TinkoffException(f'{result["errorCode"]}: {result["errorMessage"]}')

    return result['pdfUrl']


if __name__ == '__main__':
    invoice = get_invoice(
        legal_entity=LegalEntity(name='ООО Федя и Самат', inn='7722496158', kpp='772201001'),
        items=[
            Item(name='Позиция 1', price=100, amount=3),
            Item(name='Позиция 2', price=200),
        ],
    )

    print(invoice)  # noqa
