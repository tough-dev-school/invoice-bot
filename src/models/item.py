from dataclasses import dataclass


@dataclass
class Item:
    name: str
    price: int = 0
    amount: int = 0
    user_name: str = ''

    @classmethod
    def from_database(cls, database_record: dict) -> 'Item':
        return cls(
            user_name=database_record['user_name'],
            name=database_record['name'],
            price=database_record['price'],
        )

    def to_tinkoff(self) -> dict:
        return {
            'name': self.name,
            'price': self.price,
            'amount': self.amount,
            'unit': 'Шт',
            'vat': 'None',  # fuck
        }

    def __str__(self) -> str:
        return f'{self.name}, {self.amount} шт за {self.price} ₽'


DATABASE = {
    'teamlead-4-self': {
        'user_name': 'СТ-4 самостоятельный',
        'name': 'Участие в курсе «Стать Тимлидом» на плошадке education.borshev.com (тариф «самостоятельный»)',
        'price': 14_000,
    },
    'teamlead-4-full': {
        'user_name': 'СТ-4 тусовка',
        'name': 'Участие в курсе «Стать Тимлидом» на плошадке education.borshev.com (тариф «в тусовке»)',
        'price': 24_000,
    },
    'teamlead-4-vip': {
        'user_name': 'СТ-4 VIP',
        'name': 'Участие в курсе «Стать Тимлидом» на плошадке education.borshev.com (тариф «VIP»)',
        'price': 65_000,
    },
}


def get_by_slug_or_name(slug_or_name: str) -> Item | None:
    for slug, data in DATABASE.items():
        if slug == slug_or_name or data['user_name'] == slug_or_name or data['name'] == slug_or_name:
            return Item.from_database(data)


def parse_input(user_input: str) -> Item:
    item = get_by_slug_or_name(user_input)

    if item is not None:
        return item

    return Item(name=user_input)
