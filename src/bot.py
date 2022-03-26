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
from .clients.tinkoff import get_invoice
from .keyboards import keyboards as kb
from .models.item import DATABASE
from .models.item import Item
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
    update.callback_query.message.reply_text(
        text='Для начала найдем вашу организацию по ИНН.\nВведите ИНН',
    )

    context.user_data['invoice'] = {
        'legal_entity': None,  # type: ignore
        'items': [],
    }

    update.callback_query.answer()

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

    if len(entities) == 1:  # when legal entity doesn't have kpp (ИП)
        legal_entity = entities[0]
    else:
        legal_entity = [entity for entity in entities if entity.kpp == update.callback_query.data][0]

    context.user_data['invoice']['legal_entity'] = legal_entity

    update.callback_query.message.reply_text(text=f'Вы выбрали: {legal_entity}\nВсе верно?',
                                             reply_markup=kb.confirm_legal_entity_keyboard())

    return SELECT_ITEMS


def update_item_amount(callback: str, items: list[Item], update: Update, context: 'CallbackContext') -> None:
    sign = callback.split('_')[1]
    item_to_update = callback.split('_')[2]

    for item in items:
        if item.user_name != item_to_update:
            continue

        if sign == 'minus' and item.amount > 0:
            item.amount -= 1
        else:
            item.amount += 1

    update.callback_query.message.edit_text(
        text='Выберите тариф и кол-во участников',
        reply_markup=kb.select_item_keyboard(items),
    )


def item_initial_load(update: Update, context: 'CallbackContext') -> None:
    items_initial_load = [parse_input(str(item['user_name'])) for item in DATABASE.values()]

    context.user_data['invoice']['items'] = items_initial_load

    update.callback_query.message.reply_text(
        text='Выберите тариф и кол-во участников',
        reply_markup=kb.select_item_keyboard(items_initial_load),
    )


def select_item(update: Update, context: 'CallbackContext') -> int:
    callback = update.callback_query.data
    items = context.user_data['invoice']['items']

    if callback == 'approved':
        item_initial_load(update=update, context=context)
        update.callback_query.answer()
        return SELECT_ITEMS

    if callback == 'item_finish':
        selected_items = ''

        legal_entity = context.user_data['invoice']['legal_entity']

        for item in items:
            if item.amount > 0:
                selected_items += str(item) + '\n'

        update.callback_query.message.reply_text(
            text=f'Отлично, давайте все проверим.\nВы выбрали:\n{selected_items}\nЮр лицо:\n{legal_entity}\nЕсли все верно выставляем счет',
            reply_markup=kb.final_confirm_keyboard())

        update.callback_query.answer()
        return SEND_INVOICE

    # update amount of items
    update_item_amount(callback=callback, items=items, update=update, context=context)
    update.callback_query.answer()
    return SELECT_ITEMS


def send_invoice(update: Update, context: 'CallbackContext') -> int:
    items = [item for item in context.user_data['invoice']['items'] if item.amount > 0]

    legal_entity = context.user_data['invoice']['legal_entity']

    update.callback_query.message.reply_text(text=get_invoice(legal_entity=legal_entity, items=items))

    return SEND_INVOICE


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
                SELECT_ITEMS: [CallbackQueryHandler(callback=select_item, pattern='^item_.|approved')],
                SEND_INVOICE: [CallbackQueryHandler(callback=send_invoice)],
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
