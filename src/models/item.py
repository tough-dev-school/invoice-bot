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
    'aa-3-self': {
        'user_name': 'АА-3 самостоятельный',
        'name': 'Участие в курсе «Асинхронная Архитектура на плошадке education.borshev.com (тариф «самостоятельный»)',
        'price': 15_500,
    },
    'aa-3-full': {
        'user_name': 'АА-3 тусовка',
        'name': 'Участие в курсе «Асинхронная Архитектура на плошадке education.borshev.com (тариф «в тусовке»)',
        'price': 26_000,
    },
    'aa-3-vip': {
        'user_name': 'АА-3 VIP',
        'name': 'Участие в курсе «Асинхронная Архитектура на плошадке education.borshev.com (тариф «VIP»)',
        'price': 40_000,
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


if __name__ == '__main__':
    assert get_by_slug_or_name('aa-3-self') == Item(name='Участие в курсе «Асинхронная Архитектура на плошадке education.borshev.com (тариф «самостоятельный»)', price=10_000, amount=1)
    assert get_by_slug_or_name('АА-3 тусовка') == Item(name='Участие в курсе «Асинхронная Архитектура на плошадке education.borshev.com (тариф «в тусовке»)', price=20_000, amount=1)
    assert get_by_slug_or_name('Участие в курсе «Асинхронная Архитектура на плошадке education.borshev.com (тариф «VIP»)') == Item(name='Участие в курсе «Асинхронная Архитектура на плошадке education.borshev.com (тариф «VIP»)', price=32_000, amount=1)  # noqa

    assert parse_input('aa-3-self') == Item(name='Участие в курсе «Асинхронная Архитектура на плошадке education.borshev.com (тариф «самостоятельный»)', price=10_000, amount=1)
    assert parse_input('Макароны') == Item(name='Макароны', price=0, amount=1)
