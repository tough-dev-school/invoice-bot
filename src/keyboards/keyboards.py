from typing import List

from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup

from ..models.item import Item
from ..models.legal_entity import LegalEntity


def approve_buttons(text: str) -> List[List[InlineKeyboardButton]]:
    return [
        [
            InlineKeyboardButton(text=text,
                                 callback_data='approved'),
        ],
    ]


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


def confirm_legal_entity_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(approve_buttons(text='Все верно'))


def final_confirm_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(approve_buttons(text='Все верно, выставляем счет'))


def select_by_kpp_keyboard(entities: list[LegalEntity]) -> InlineKeyboardMarkup:
    buttons = []

    for entity in entities:
        buttons.append(
            [
                InlineKeyboardButton(text=entity.name,
                                     callback_data=entity.kpp),
            ],
        )

    return InlineKeyboardMarkup(buttons)


def select_item_keyboard(items: list[Item]) -> InlineKeyboardMarkup:
    buttons = []

    for item in items:
        buttons.append(
            [
                InlineKeyboardButton(text=f'{item.user_name}, цена: {item.price}р.',
                                     callback_data=str(item.user_name)),
            ],
        )
        buttons.append(
            [
                InlineKeyboardButton(text='-',
                                     callback_data='item_minus_' + item.user_name),
                InlineKeyboardButton(text=f'{item.amount} шт.',
                                     callback_data='...'),
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
