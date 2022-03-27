from typing import List

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from ..models.item import Item
from ..models.legal_entity import LegalEntity


def return_to_main_menu_button(text: str = 'В меню') -> List[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(text=text,
                             callback_data='main_menu'),
    ]


def approve_button(text: str) -> List[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(text=text,
                             callback_data='approved'),
    ]


def edit_button(text: str, previous_step: str) -> List[InlineKeyboardButton]:
    return [
        InlineKeyboardButton(text=text,
                             callback_data='return_to_' + previous_step),
    ]


def wrong_inn_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        edit_button(text='Ввести инн заново',
                    previous_step='legal_entity'),
    ])


def main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text='Сформируем счет',
                                 callback_data='invoice'),
        ],
        [
            InlineKeyboardButton(text='Выставим акт (WIP)',
                                 callback_data='act'),
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def confirm_legal_entity_and_get_invoice_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        approve_button(text='Все верно, выставляем счет!'),
        edit_button(text='Изменить юр.лицо',
                    previous_step='legal_entity'),
    ]
    return InlineKeyboardMarkup(buttons)


def confirm_items_keyboard(show_approve: bool) -> InlineKeyboardMarkup:
    buttons = []
    if show_approve:
        buttons.append(approve_button(text='Все верно'))

    buttons.append(edit_button(text='Поменять кол-во',
                               previous_step='select_item'))

    return InlineKeyboardMarkup(buttons)


def select_by_kpp_keyboard(entities: list[LegalEntity]) -> InlineKeyboardMarkup:
    buttons = []

    for entity in entities:
        if entity.kpp is None:
            kpp_for_callback = 0
        else:
            kpp_for_callback = entity.kpp

        buttons.append(
            [
                InlineKeyboardButton(text=entity.name,
                                     callback_data=kpp_for_callback),
            ],
        )

    return InlineKeyboardMarkup(buttons)


def select_course_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text='Асинхронная архитектура',  # replace hardcode
                                 callback_data='course_aa'),
        ],
    ]

    return InlineKeyboardMarkup(buttons)


def select_item_keyboard(items: list[Item]) -> InlineKeyboardMarkup:
    buttons = []

    for item in items:
        buttons.append(
            [
                InlineKeyboardButton(text=f'{item.user_name}, цена: {item.price}р.',
                                     callback_data='item_noaction'),
            ],
        )
        buttons.append(
            [
                InlineKeyboardButton(text='-',
                                     callback_data='item_minus_' + item.user_name),
                InlineKeyboardButton(text=f'{item.amount} шт.',
                                     callback_data='item_noaction'),
                InlineKeyboardButton(text='+',
                                     callback_data='item_plus_' + item.user_name),
            ],
        )

    buttons.append(
        [
            InlineKeyboardButton(text='Готово',
                                 callback_data='item_finish'),
        ],
    )

    return InlineKeyboardMarkup(buttons)


def link_to_invoice_keyboard(url: str) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text='Скачать счет',
                                 url=url),
        ],
        return_to_main_menu_button(),
    ]

    return InlineKeyboardMarkup(buttons)
