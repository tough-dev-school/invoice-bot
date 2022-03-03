import logging
import os

from telegram import ReplyKeyboardMarkup
from telegram import Update
from telegram.ext import CallbackContext
from telegram.ext import CommandHandler
from telegram.ext import ConversationHandler
from telegram.ext import Dispatcher
from telegram.ext import Filters
from telegram.ext import MessageHandler
from telegram.ext import Updater

from dadata_client import get_by_inn
from item import DATABASE
from item import parse_input

INN, CONFIRM_LEGAL_ENTITY, ADD_ITEM, CHANGE_PRICE_OR_AMOUNT_OF_LAST_ITEM = range(4)


def enable_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    )


def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text('Введите ИНН')

    context.user_data['invoice'] = {}

    return INN


def inn(update: Update, context: CallbackContext) -> int | None:
    inn: str = update.message.text

    entities = get_by_inn(inn)

    match len(entities):
        case 0:
            update.message.reply_text('Чё-т ничего не нашлось :( Попробуйте ещё раз или напишите Феде')
            return
        case 1:
            context.user_data['invoice']['legal_entity'] = entities[0]
            update.message.reply_text(
                text=f'{entities[0]}. Если ошиблись — наберите /start',
                reply_markup=ReplyKeyboardMarkup([[i['user_name']] for i in DATABASE.values()]),
            )
            return ADD_ITEM


def add_item(update: Update, context: CallbackContext) -> int:
    item = parse_input(update.message.text)
    context.user_data['invoice']['item'] = item

    legal_entity = context.user_data['invoice']['legal_entity']

    update.message.reply_text(
        text=f'Ок, {item}. Выставляем на {legal_entity.name}? Если хотите поменять цену или количество — напишите мне.',
        reply_markup=ReplyKeyboardMarkup([['Выставляем!']]),
    )

    return CHANGE_PRICE_OR_AMOUNT_OF_LAST_ITEM


def change_price_or_amount_of_last_item(update: Update, context: CallbackContext) -> None:
    number = int(update.message.text)

    if number < 100:
        context.user_data['invoice']['item'].amount = number
    else:
        context.user_data['invoice']['item'].price = number

    item = context.user_data['invoice']['item']
    legal_entity = context.user_data['invoice']['legal_entity']

    update.message.reply_text(
        text=f'Ок, {item}. Выставляем на {legal_entity.name}? Если хотите поменять цену или количество — напишите мне.',
        reply_markup=ReplyKeyboardMarkup([['Выставляем!']]),
    )


def main() -> None:
    bot_token = os.getenv('TELEGRAM_TOKEN')

    if bot_token is None:
        raise RuntimeError('Please set TELEGRAM_TOKEN env var')

    bot = Updater(token=bot_token)
    dispatcher: Dispatcher = bot.dispatcher  # type: ignore

    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler('start', callback=start)],
            states={
                INN: [MessageHandler(callback=inn, filters=Filters.text)],
                ADD_ITEM: [MessageHandler(callback=add_item, filters=Filters.text)],
                CHANGE_PRICE_OR_AMOUNT_OF_LAST_ITEM: [MessageHandler(callback=change_price_or_amount_of_last_item, filters=Filters.text)],
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
