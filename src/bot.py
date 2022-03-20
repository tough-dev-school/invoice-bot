import logging
import os
from typing import TYPE_CHECKING

from telegram import Update
from telegram.ext import CallbackQueryHandler
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Dispatcher
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from .clients.dadata import get_by_inn
from .keyboards import keyboards as kb
from .models.item import DATABASE
from .models.item import parse_input

MAIN_MENU, INN, CONFIRM_LEGAL_ENTITY, SELECT_COURSE, SELECT_ITEMS, SEND_INVOICE = range(6)

if TYPE_CHECKING:
    from .t import CallbackContext


def enable_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )


def main_menu(update: Update, context: 'CallbackContext') -> int:
    update.message.reply_text(
        text='Что будем делать?',
        reply_markup=kb.main_menu_keyboard(),
    )

    return MAIN_MENU


def start_invoice(update: Update, context: 'CallbackContext') -> int:
    query = update.callback_query

    query.message.reply_text(
        text='Для начала найдем вашу организацию по ИНН.\nВведите ИНН',
        # reply_markup=kb.navigation_only_keyboard(previous_step='main_menu'),
    )

    context.user_data['invoice'] = {
        'legal_entity': None,  # type: ignore
        'items': [],
    }

    query.answer()

    update.callback_query.message.edit_reply_markup()

    return INN


def inn(update: Update, context: 'CallbackContext') -> int | None:
    inn: str = update.message.text

    context.user_data['entities'] = get_by_inn(inn)

    if len(context.user_data['entities']) > 0:
        update.message.reply_text(
            text='Мы нашли вот эти организации, выберите вашу',
            reply_markup=kb.select_by_kpp_keyboard(entities=context.user_data['entities']),
        )

        return CONFIRM_LEGAL_ENTITY

    if len(context.user_data['entities']) == 0:
        update.message.reply_text('Чё-т ничего не нашлось :( Попробуйте ещё раз или напишите Феде')


def confirm_legal_entity(update: Update, context: 'CallbackContext') -> int:
    entities = context.user_data['entities']

    if len(entities) == 1:
        legal_entity = entities[0]
    else:
        legal_entity = [entity for entity in entities if entity.kpp == update.callback_query.data][0]

    context.user_data['invoice']['legal_entity'] = legal_entity

    update.callback_query.message.reply_text(text=f'Вы выбрали: {legal_entity}\nВсе верно?',
                                             reply_markup=kb.confirm_legal_entity_keyboard(previous_step='inn'))

    update.callback_query.message.edit_reply_markup()

    return SELECT_ITEMS


def select_item(update: Update, context: 'CallbackContext') -> int:
    if update.callback_query.data.split('_')[1] == 'ok':
        items_initial_load = [parse_input(i['user_name']) for i in DATABASE.values()]

        context.user_data['invoice']['items'] = items_initial_load

        update.callback_query.message.reply_text(
            text='Выберите тариф и кол-во участников',
            reply_markup=kb.select_item_keyboard(items_initial_load),
        )

    items = context.user_data['invoice']['items']

    if update.callback_query.data.split('_')[1] == 'minus':
        for item in items:
            if item.user_name == update.callback_query.data.split('_')[2] and item.amount > 0:
                item.amount -= 1

        update.callback_query.message.edit_text(
            text='Выберите тариф и кол-во участников',
            reply_markup=kb.select_item_keyboard(items),
        )

    if update.callback_query.data.split('_')[1] == 'plus':
        for item in items:
            if item.user_name == update.callback_query.data.split('_')[2]:
                item.amount += 1

        update.callback_query.message.edit_text(
            text=f'Выберите курс и количество билетов',
            reply_markup=kb.select_item_keyboard(items),
        )

    update.callback_query.answer()

    if update.callback_query.data.split('_')[1] == 'finish':
        selected_items = ''

        legal_entity = context.user_data['invoice']['legal_entity']

        for item in items:
            if item.amount > 0:
                selected_items += str(item) + '\n'

        update.callback_query.message.reply_text(
            text=f'Отлично, давайте все проверим.\nВы выбрали:\n{selected_items}\nЮр лицо:\n{legal_entity}\nЕсли все верно выставляем счет',
            reply_markup=kb.final_confirm_keyboard(previous_step='select_item'))

        update.callback_query.message.edit_reply_markup()

        return SEND_INVOICE
    else:
        return SELECT_ITEMS


def send_invoice(update: Update, context: 'CallbackContext') -> None:
    item = context.user_data['invoice']['items'][0]
    legal_entity = context.user_data['invoice']['legal_entity']

    update.message.reply_text(
        text=f'Ок, {item}. Выставляем на {legal_entity.name}? Если хотите поменять цену или количество — напишите мне.',
        # reply_markup=ReplyKeyboardMarkup([['Выставляем!']]),
    )


def main() -> None:
    bot_token = os.getenv('TELEGRAM_TOKEN')

    if bot_token is None:
        raise RuntimeError('Please set TELEGRAM_TOKEN env var')

    bot = Updater(token=bot_token)
    dispatcher: Dispatcher = bot.dispatcher  # type: ignore

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('start', callback=main_menu)],
            states={
                MAIN_MENU: [CallbackQueryHandler(callback=start_invoice, pattern='invoice')],
                INN: [MessageHandler(callback=inn, filters=Filters.text)],
                CONFIRM_LEGAL_ENTITY: [CallbackQueryHandler(callback=confirm_legal_entity)],
                SELECT_ITEMS: [CallbackQueryHandler(callback=select_item, pattern='^item_.')],
                SEND_INVOICE: [CallbackQueryHandler(callback=send_invoice, ),
                               ],
            },
            fallbacks=[],
            allow_reentry=True,
        ),
    )

    enable_logging()
    bot.start_polling()


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv()

    main()
