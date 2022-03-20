from telegram import InlineKeyboardButton
from telegram import InlineKeyboardMarkup


def navigation_buttons(previous_step: str):
    return [
        [
            InlineKeyboardButton(text='В меню',
                                 callback_data='navi_main_menu'),
            InlineKeyboardButton(text='Назад',
                                 callback_data='navi_' + previous_step),
        ],
    ]


def approve_buttons(previous_step: str):
    return [
        [
            InlineKeyboardButton(text='Все верно',
                                 callback_data='item_ok'),
        ],
    ]


def navigation_only_keyboard(previous_step: str):
    return InlineKeyboardMarkup(navigation_buttons(previous_step))


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


def confirm_legal_entity_keyboard(previous_step: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(approve_buttons(previous_step))


def final_confirm_keyboard(previous_step: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(approve_buttons(previous_step))


def select_by_kpp_keyboard(entities) -> InlineKeyboardMarkup:
    buttons = []

    for entity in entities:
        buttons.append(
            [
                InlineKeyboardButton(text=entity.name,
                                     callback_data=entity.kpp),
            ],
        )

    # buttons.append(navigation_buttons(previous_step='inn')[0])

    return InlineKeyboardMarkup(buttons)


def select_item_keyboard(items) -> InlineKeyboardMarkup:
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
                                     callback_data='ss'),
                InlineKeyboardButton(text='+',
                                     callback_data='item_plus_' + item.user_name),
            ],
        )

    buttons.append(
        [
            InlineKeyboardButton(text='Готов',
                                 callback_data='item_finish'),
        ],
    )
    # buttons.append(navigation_buttons(previous_step='inn')[0])

    return InlineKeyboardMarkup(buttons)
