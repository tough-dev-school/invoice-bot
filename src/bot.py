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

MAIN_MENU, SELECT_COURSE, SELECT_ITEMS, FIND_LEGAL_ENTITY, SELECT_LEGAL_ENTITY, CONFIRM_LEGAL_ENTITY, SEND_INVOICE = range(
    7)

if TYPE_CHECKING:
    from .t import CallbackContext


def enable_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )


def button_main_menu(update: Update, context: 'CallbackContext') -> int:
    update.callback_query.message.reply_text(
        text='Привет! Я бот-помощник Школы сильных программистов. '
             'С моей помощью вы можете получить счет для оплаты '
             'обучения сотрудников от юрлица',
        reply_markup=kb.main_menu_keyboard(),
    )
    return SELECT_COURSE


def command_main_menu(update: Update, context: 'CallbackContext') -> int:
    update.message.reply_text(
        text='Привет! Я бот-помощник Школы сильных программистов. '
             'С моей помощью вы можете получить счет для оплаты '
             'обучения сотрудников от юрлица',
        reply_markup=kb.main_menu_keyboard(),
    )
    return SELECT_COURSE


def select_course(update: Update, context: 'CallbackContext') -> int:
    update.callback_query.message.reply_text(
        text='Доступ к какому курсу вы хотите приобрести?',
        reply_markup=kb.select_course_keyboard(),
    )

    update.callback_query.answer()

    return SELECT_ITEMS


def item_initial_load(update: Update, context: 'CallbackContext') -> None:
    context.user_data['invoice'] = {
        'legal_entity': None,  # type: ignore
        'items': [],
    }

    items_initial_load = [parse_input(str(item['user_name'])) for item in DATABASE.values()]

    context.user_data['invoice']['items'] = items_initial_load

    update.callback_query.message.reply_text(
        text='Выберите тариф и кол-во участников',
        reply_markup=kb.select_item_keyboard(items_initial_load),
    )


def update_item_amount(callback: str, items: list[Item], update: Update, context: 'CallbackContext') -> None:
    sign = callback.split('_')[1]
    item_to_update = callback.split('_')[2]

    for item in items:
        if item.user_name != item_to_update:
            continue

        if sign == 'minus' and item.amount > 0:
            item.amount -= 1
        elif sign == 'plus':
            item.amount += 1

    update.callback_query.answer()

    update.callback_query.message.edit_text(
        text='Выберите тариф и кол-во участников',
        reply_markup=kb.select_item_keyboard(items),
    )


def item_confirm_message(update: Update, context: 'CallbackContext', items: list[Item]) -> None:
    selected_items = ''
    total_amount = 0

    for item in items:
        if item.amount > 0:
            selected_items += str(item) + '\n'

            total_amount += item.amount * item.price

    if total_amount == 0:
        text = 'Похоже вы ничего не выбрали'
        show_approve = False
    else:
        text = f'Отлично, давайте проверим.\n\nВы выбрали:\n\n{selected_items}\n\n' \
               f'Итоговая сумма: {total_amount}\n\nВсе верно?'
        show_approve = True

    update.callback_query.message.reply_text(
        text=text,
        reply_markup=kb.confirm_items_keyboard(show_approve=show_approve))


def select_item(update: Update, context: 'CallbackContext') -> int:
    callback = update.callback_query.data

    # initial load of items
    if callback == 'course_aa':
        item_initial_load(update=update, context=context)
        update.callback_query.answer()
        return SELECT_ITEMS

    # buttons with no action
    if callback == 'item_noaction':
        update.callback_query.answer()
        return SELECT_ITEMS

    items = context.user_data['invoice']['items']

    # "Готово" button
    if callback == 'item_finish':
        item_confirm_message(update=update,
                             context=context,
                             items=items)
        update.callback_query.answer()
        return FIND_LEGAL_ENTITY

    # update amount of items
    update_item_amount(callback=callback, items=items, update=update, context=context)
    update.callback_query.answer()
    return SELECT_ITEMS


def find_legal_entity_by_inn(update: Update, context: 'CallbackContext') -> int:
    update.callback_query.message.reply_text(
        text='Введите ИНН компании, чтобы мы могли выставить вам счет',
    )

    update.callback_query.answer()

    return SELECT_LEGAL_ENTITY


def select_legal_entity_by_kpp(update: Update, context: 'CallbackContext') -> int | None:
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

        return SELECT_LEGAL_ENTITY


def confirm_legal_entity(update: Update, context: 'CallbackContext') -> int:
    entities = context.user_data['entities']

    if len(entities) == 1:  # when legal entity doesn't have kpp (ИП)
        legal_entity = entities[0]
    else:
        legal_entity = [entity for entity in entities if entity.kpp == update.callback_query.data][0]

    context.user_data['invoice']['legal_entity'] = legal_entity

    update.callback_query.message.reply_text(text=f'Вы выбрали: {legal_entity}\nВсе верно?',
                                             reply_markup=kb.confirm_legal_entity_and_get_invoice_keyboard())

    return SEND_INVOICE


def send_invoice(update: Update, context: 'CallbackContext') -> int:
    items = [item for item in context.user_data['invoice']['items'] if item.amount > 0]

    legal_entity = context.user_data['invoice']['legal_entity']

    text = 'Ура! Вас счет готов.' \
           'Если возникли ошибки — напишите пожалуйста на support@education.borshev.com.'

    update.callback_query.message.reply_text(text=text,
                                             reply_markup=kb.link_to_invoice_keyboard(
                                                 url=get_invoice(legal_entity=legal_entity,
                                                                 items=items)))

    return MAIN_MENU


def main() -> None:
    bot_token = os.getenv('TELEGRAM_TOKEN')

    if bot_token is None:
        raise RuntimeError('Please set TELEGRAM_TOKEN env var')

    bot = Updater(token=bot_token)
    dispatcher: Dispatcher = bot.dispatcher  # type: ignore

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('start', callback=command_main_menu)],
            states={
                SELECT_COURSE: [CallbackQueryHandler(callback=select_course, pattern='invoice')],
                SELECT_ITEMS: [CallbackQueryHandler(callback=select_item, pattern='^item_.|course_aa')],
                FIND_LEGAL_ENTITY: [CallbackQueryHandler(callback=find_legal_entity_by_inn, pattern='approved')],
                SELECT_LEGAL_ENTITY: [MessageHandler(callback=select_legal_entity_by_kpp, filters=Filters.text)],
                CONFIRM_LEGAL_ENTITY: [CallbackQueryHandler(callback=confirm_legal_entity)],
                SEND_INVOICE: [CallbackQueryHandler(callback=send_invoice, pattern='approved')],
            },
            fallbacks=[
                CallbackQueryHandler(callback=button_main_menu, pattern='main_menu'),
                CallbackQueryHandler(callback=find_legal_entity_by_inn, pattern='return_to_legal_entity'),
                CallbackQueryHandler(callback=select_item, pattern='return_to_select_item'),
            ],
            allow_reentry=True,
        ),
    )

    enable_logging()
    bot.start_polling()


if __name__ == '__main__':
    from dotenv import load_dotenv

    load_dotenv()

    main()
