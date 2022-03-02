from dataclasses import dataclass


@dataclass
class Item:
    name: str
    price: int
    amount: int | None = 1

    def to_tinkoff(self) -> dict:
        return {
            'name': self.name,
            'price': self.price,
            'amount': self.amount,
            'unit': 'Шт',
            'vat': 'None',  # fuck
        }
